from fastapi import FastAPI, Form, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import List, Dict, Any
import traceback
from PIL import Image, ImageFilter
from torchvision.transforms import functional as TF
from math import ceil, floor
import asyncio
import numpy as np
import json
from fastapi import File, UploadFile, Form, HTTPException
from fastapi.param_functions import File
from pydantic import BaseModel
import torchvision
import torchvision.transforms as T  
from typing import Optional
import os
import numpy as np
import torch
import cv2 as cv
import base64
import io
import loader 
import uvicorn
from GroundingDINO.groundingdino.util import box_ops
from GroundingDINO.groundingdino.util.inference import annotate, load_image, predict
from simple_lama_inpainting import SimpleLama
from gemini import *
import random

os.environ["TOKENIZERS_PARALLELISM"] = "false"

BOX_TRESHOLD = 0.35
TEXT_TRESHOLD = 0.25
NUM_INFERENCE_STEP = 50
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

grounding_dino_args = {
    'device': 'cpu',
    'filename': 'groundingdino_swinb_cogcoor.pth',
    'ckpt_config_filename': 'GroundingDINO_SwinB.cfg.py',
}

sam_args = {
    'ckpt': 'weights/sam_vit_h_4b8939.pth',
    'device': DEVICE,
}

# controlnet_args = {
#     'stable_diffusion_name': 'SG161222/Realistic_Vision_V5.1_noVAE',
#     'controlnet_name': 'lllyasviel/control_v11p_sd15_inpaint', 
#     'device': DEVICE,
# }

diffuser_args = {
    'model_id': 'stabilityai/stable-diffusion-2-1',
    'device': DEVICE,
}

powerpaint_args = {
    'stable_inpaint_name': 'runwayml/stable-diffusion-inpainting',
    'stable_diffusion_name': 'runwayml/stable-diffusion-v1-5',
    'device': DEVICE,
}

class ImageManipulationRequest(BaseModel):
    image: str 
    instruction: str
    
class ImageObjectRemovalRequest(BaseModel):
    image: str 
    instruction: str
    negative: str

class ExpandRequest(BaseModel):
    image: str
    vertical_expansion_ratio: float
    horizontal_expansion_ratio: float

detection_model = loader.getGroundingDINO(**grounding_dino_args)
segmenter = loader.getSAM(**sam_args)
painter = loader.getPowerPaint(**powerpaint_args)
GEMINI_MODEL_NAME = 'gemini-pro'  # Replace with your model name
GEMINI_API_KEY = 'YOUR_API_KEY'  # Replace with your API key
gemini_generator = GeminiGenerator(model_name=GEMINI_MODEL_NAME, api_key=GEMINI_API_KEY)
gemini_generator.load_prefix('resources/viedit.txt')

def detect(image: np.array, instruction: str):
    image_source = Image.fromarray(image)
    image_pt = loader.rescale_on_range(image, return_type='pt')
    boxes, logits, phrases = predict(
        model=detection_model, 
        image=image_pt, 
        caption=str(instruction), 
        box_threshold=BOX_TRESHOLD, 
        text_threshold=TEXT_TRESHOLD,
    )
    if len(boxes) == 0:
        return torch.zeros((1, 4))  
    else:
        W, H = image_source.size  
        boxes_xyxy = box_ops.box_cxcywh_to_xyxy(boxes) * torch.Tensor([W, H, W, H])
        return boxes_xyxy

def segment(image: np.array, instruction: str):
    image_source = Image.fromarray(image)
    image_source = loader.rescale_on_range(image_source, return_type='np')
    segmenter.set_image(image_source)
    boxes_xyxy = detect(image, instruction)
    transformed_boxes = segmenter.transform.apply_boxes_torch(boxes_xyxy, image_source.shape[:2]).to(DEVICE)
    masks, _, _ = segmenter.predict_torch(
        point_coords = None,
        point_labels = None,
        boxes = transformed_boxes,
        multimask_output = False,
    )
    final_mask = torch.sum(masks, dim=0,dtype=torch.bool)
    image_mask = final_mask[0].cpu().numpy() 
    image_mask = image_mask.astype(np.uint8)
    image_mask *= 255
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(15,15))
    image_mask = cv.morphologyEx(image_mask, cv.MORPH_OPEN, kernel)
    image_mask = cv.morphologyEx(image_mask, cv.MORPH_OPEN, kernel)
    image_source_for_inpaint = Image.fromarray(image_source)
    image_mask_for_inpaint = Image.fromarray(image_mask)
    print(image_mask.shape)
    return image_mask_for_inpaint

def masking(image: np.array, instruction: str):
    image_source = Image.fromarray(image)
    image_source = loader.rescale_on_range(image_source, return_type='np')
    segmenter.set_image(image_source)
    boxes_xyxy = detect(image, instruction)
    transformed_boxes = segmenter.transform.apply_boxes_torch(boxes_xyxy, image_source.shape[:2]).to(DEVICE)
    masks, _, _ = segmenter.predict_torch(
        point_coords = None,
        point_labels = None,
        boxes = transformed_boxes,
        multimask_output = False,
    )
    final_mask = torch.sum(masks, dim=0,dtype=torch.bool)
    image_mask = final_mask[0].cpu().numpy() 
    image_mask = image_mask.astype(np.uint8)
    image_mask *= 255
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(15,15))
    image_mask = cv.morphologyEx(image_mask, cv.MORPH_OPEN, kernel)
    dilate_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (25, 25)) 
    image_mask = cv.dilate(image_mask, dilate_kernel, iterations=2)  
    image_mask = cv.morphologyEx(image_mask, cv.MORPH_OPEN, kernel)
    image_source_for_inpaint = Image.fromarray(image_source)
    image_mask_for_inpaint = Image.fromarray(image_mask)
    return image_mask_for_inpaint

def delete(image_array: np.array, instruction: str, negative: str, device: str = 'cuda'):
    image_source = Image.fromarray(image_array)
    image_main = Image.fromarray(image_array)
    image_source = loader.rescale_on_range(image_source, return_type='np')
    image = loader.rescale_on_range(image_source, return_type='pt')
    image_mask_for_inpaint = masking(image_array, instruction)
    negative_template = negative

    TARGET_PROMPT_A = 'an empty' + ' P_ctxt'
    TARGET_PROMPT_B = 'an empty' + ' P_ctxt'
    NEG_PROMT_A = negative_template + ' P_obj'
    NEG_PROMT_B = negative_template + ' P_obj'

    size1, size2 = image_main.convert('RGB').size
    if size1 < size2:
        image_main = image_main.convert('RGB').resize((640, int(size2 / size1 * 640)))
        image_mask_for_inpaint = image_mask_for_inpaint.convert('RGB').resize((640, int(size2 / size1 * 640)))
    else:
        image_main = image_main.convert('RGB').resize((int(size1 / size2 * 640), 640))
        image_mask_for_inpaint = image_mask_for_inpaint.convert('RGB').resize((int(size1 / size2 * 640), 640))

    img = np.array(image_main.convert('RGB'))
    W = int(np.shape(img)[0] - np.shape(img)[0] % 8)
    H = int(np.shape(img)[1] - np.shape(img)[1] % 8)
    image_main = image_main.resize((H, W))
    image_mask_for_inpaint = image_mask_for_inpaint.resize((H, W))

    torch.manual_seed(2422003)
    torch.cuda.manual_seed(2422003)
    torch.cuda.manual_seed_all(2422003)
    np.random.seed(2422003)
    random.seed(2422003)

    result = painter(
        promptA=TARGET_PROMPT_A,
        promptB=TARGET_PROMPT_B,
        tradoff=1,
        tradoff_nag=1,  
        negative_promptA=NEG_PROMT_A,
        negative_promptB=NEG_PROMT_B,
        image=image_main.convert('RGB'),
        mask_image=image_mask_for_inpaint.convert('RGB'),
        width=H,
        height=W,
        guidance_scale=15,  
        num_inference_steps=50 
    ).images[0]
    mask_np = np.array(image_mask_for_inpaint.convert('RGB'))
    red = np.array(result).astype('float') * 1
    red[:, :, 0] = 180.0
    red[:, :, 2] = 0
    red[:, :, 1] = 0
    result_m = np.array(result)
    result_m = Image.fromarray(
        (result_m.astype('float') * (1 - mask_np.astype('float') / 512.0) +
         mask_np.astype('float') / 512.0 * red).astype('uint8'))
    m_img = image_mask_for_inpaint.convert('RGB').filter(ImageFilter.GaussianBlur(radius=10))
    m_img = np.asarray(m_img) / 255.0
    img_np = np.asarray(image_main.convert('RGB')) / 255.0
    ours_np = np.asarray(result) / 255.0
    ours_np = ours_np * m_img + (1 - m_img) * img_np
    result_paste = Image.fromarray(np.uint8(ours_np * 255))
    return np.array(result_paste)

def edit(image_array: np.array, user_instruction: str, device: str='cuda'):
    image_source = Image.fromarray(image_array)
    image_main = Image.fromarray(image_array)
    image_source = loader.rescale_on_range(image_source, return_type='np')
    image = loader.rescale_on_range(image_source, return_type='pt')
    SOURCE_PROMPT, TARGET_PROMPT = gemini_generator.call_gemini(user_instruction)
    boxes, logits, phrases = predict(
        model=detection_model, 
        image=image, 
        caption=str(SOURCE_PROMPT), 
        box_threshold=BOX_TRESHOLD, 
        text_threshold=TEXT_TRESHOLD,
    )
    
    if len(boxes) == 0:
        print("No objects detected. Returning the original image.")
        return np.array(image_source)
    
    segmenter.set_image(image_source)
    H, W, _ = image_source.shape
    boxes_xyxy = box_ops.box_cxcywh_to_xyxy(boxes) * torch.Tensor([W, H, W, H])
    transformed_boxes = segmenter.transform.apply_boxes_torch(boxes_xyxy, image_source.shape[:2]).to(DEVICE)
    masks, _, _ = segmenter.predict_torch(
        point_coords = None,
        point_labels = None,
        boxes = transformed_boxes,
        multimask_output = False,
    )
    final_mask = torch.sum(masks, dim=0, dtype=torch.bool)
    image_mask = final_mask[0].cpu().numpy() 
    image_mask = image_mask.astype(np.uint8)
    image_mask *= 255
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(15,15))
    image_mask = cv.morphologyEx(image_mask, cv.MORPH_OPEN, kernel)
    dilate_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (25, 25)) 
    image_mask = cv.dilate(image_mask, dilate_kernel, iterations=2)  
    image_mask = cv.morphologyEx(image_mask, cv.MORPH_OPEN, kernel)
    image_source_for_inpaint = Image.fromarray(image_source)
    image_mask_for_inpaint = Image.fromarray(image_mask)
    negative_template = 'blurry, unreal, disproportioned, dismembered, duplicate, deformed, malformed'

    TARGET_PROMPT_A = TARGET_PROMPT + ' P_obj'
    TARGET_PROMPT_B = TARGET_PROMPT + ' P_obj'
    NEG_PROMT_A = negative_template + ' P_obj'
    NEG_PROMT_B = negative_template + ' P_obj'

    size1, size2 = image_main.convert('RGB').size
    if size1 < size2:
        image_main = image_main.convert('RGB').resize((640, int(size2 / size1 * 640)))
        image_mask_for_inpaint = image_mask_for_inpaint.convert('RGB').resize((640, int(size2 / size1 * 640)))
    else:
        image_main = image_main.convert('RGB').resize((int(size1 / size2 * 640), 640))
        image_mask_for_inpaint = image_mask_for_inpaint.convert('RGB').resize((int(size1 / size2 * 640), 640))

    img = np.array(image_main.convert('RGB'))
    W = int(np.shape(img)[0] - np.shape(img)[0] % 8)
    H = int(np.shape(img)[1] - np.shape(img)[1] % 8)
    image_main = image_main.resize((H, W))
    image_mask_for_inpaint = image_mask_for_inpaint.resize((H, W))

    torch.manual_seed(2422003)
    torch.cuda.manual_seed(2422003)
    torch.cuda.manual_seed_all(2422003)
    np.random.seed(2422003)
    random.seed(2422003)

    result = painter(
        promptA=TARGET_PROMPT_A,
        promptB=TARGET_PROMPT_B,
        tradoff=1,
        tradoff_nag=1,  
        negative_promptA=NEG_PROMT_A,
        negative_promptB=NEG_PROMT_B,
        image=image_main.convert('RGB'),
        mask_image=image_mask_for_inpaint.convert('RGB'),
        width=H,
        height=W,
        guidance_scale=15,  
        num_inference_steps=50 
    ).images[0]
    mask_np = np.array(image_mask_for_inpaint.convert('RGB'))
    red = np.array(result).astype('float') * 1
    red[:, :, 0] = 180.0
    red[:, :, 2] = 0
    red[:, :, 1] = 0
    result_m = np.array(result)
    result_m = Image.fromarray(
        (result_m.astype('float') * (1 - mask_np.astype('float') / 512.0) +
         mask_np.astype('float') / 512.0 * red).astype('uint8'))
    m_img = image_mask_for_inpaint.convert('RGB').filter(ImageFilter.GaussianBlur(radius=10))
    m_img = np.asarray(m_img) / 255.0
    img_np = np.asarray(image_main.convert('RGB')) / 255.0
    ours_np = np.asarray(result) / 255.0
    ours_np = ours_np * m_img + (1 - m_img) * img_np
    result_paste = Image.fromarray(np.uint8(ours_np * 255))
    return np.array(result_paste)

def expand(image_array: np.array, vertical_expansion_ratio: float, horizontal_expansion_ratio: float):  
    image_source = Image.fromarray(image_array)
    image_main = Image.fromarray(image_array)
    
    negative_template = 'blurry, unreal, disproportioned, dismembered, duplicate, deformed, malformed'
    TARGET_PROMPT_A = ' P_ctxt'
    TARGET_PROMPT_B = ' P_ctxt'
    NEG_PROMT_A = negative_template + ' P_obj'
    NEG_PROMT_B = negative_template + ' P_obj'
        
    o_W, o_H = image_main.convert('RGB').size 
    c_W = int(horizontal_expansion_ratio * o_W)
    c_H = int(vertical_expansion_ratio * o_H)

    expand_img = np.ones((c_H, c_W, 3), dtype=np.uint8) * 127
    original_img = image_array
    expand_img[int((c_H - o_H) / 2.0):int((c_H - o_H) / 2.0) + o_H,
    int((c_W - o_W) / 2.0):int((c_W - o_W) / 2.0) + o_W, :] = original_img

    blurry_gap = 10

    expand_mask = np.ones((c_H, c_W, 3), dtype=np.uint8) * 255
    if vertical_expansion_ratio == 1 and horizontal_expansion_ratio != 1:
        expand_mask[int((c_H - o_H) / 2.0):int((c_H - o_H) / 2.0) + o_H,
        int((c_W - o_W) / 2.0) + blurry_gap:int((c_W - o_W) / 2.0) + o_W - blurry_gap, :] = 0
    elif vertical_expansion_ratio != 1 and horizontal_expansion_ratio != 1:
        expand_mask[int((c_H - o_H) / 2.0) + blurry_gap:int((c_H - o_H) / 2.0) + o_H - blurry_gap,
        int((c_W - o_W) / 2.0) + blurry_gap:int((c_W - o_W) / 2.0) + o_W - blurry_gap, :] = 0
    elif vertical_expansion_ratio != 1 and horizontal_expansion_ratio == 1:
        expand_mask[int((c_H - o_H) / 2.0) + blurry_gap:int((c_H - o_H) / 2.0) + o_H - blurry_gap,
        int((c_W - o_W) / 2.0):int((c_W - o_W) / 2.0) + o_W, :] = 0

    expand_img = Image.fromarray(expand_img)
    expand_mask = Image.fromarray(expand_mask)
    
    size1, size2 = expand_img.convert('RGB').size 
    if size1 < size2:
        target_size = (512, int(size2 / size1 * 512))
    else:
        target_size = (int(size1 / size2 * 512), 512)
    
    expand_img = expand_img.convert('RGB').resize(target_size)
    expand_mask = expand_mask.convert('RGB').resize(target_size)
    
    img = np.array(expand_img)
    W = int(np.shape(img)[0] - np.shape(img)[0] % 8)
    H = int(np.shape(img)[1] - np.shape(img)[1] % 8)
    expand_img = expand_img.resize((H, W))
    expand_mask = expand_mask.resize((H, W))
    
    torch.manual_seed(2422003)
    torch.cuda.manual_seed(2422003)
    torch.cuda.manual_seed_all(2422003)
    np.random.seed(2422003)
    random.seed(2422003)

    result = painter(
        promptA=TARGET_PROMPT_A,
        promptB=TARGET_PROMPT_B,
        tradoff=1,
        tradoff_nag=1,  
        negative_promptA=NEG_PROMT_A,
        negative_promptB=NEG_PROMT_B,
        image=expand_img.convert('RGB'),
        mask_image=expand_mask.convert('RGB'),
        width=H,
        height=W,
        guidance_scale=15,  
        num_inference_steps=50 
    ).images[0]
    
    mask_np = np.array(expand_mask.convert('RGB'))
    red = np.array(result).astype('float') * 1
    red[:, :, 0] = 180.0
    red[:, :, 2] = 0
    red[:, :, 1] = 0
    result_m = np.array(result)
    result_m = Image.fromarray(
        (result_m.astype('float') * (1 - mask_np.astype('float') / 512.0) +
        mask_np.astype('float') / 512.0 * red).astype('uint8'))
    
    m_img = expand_mask.convert('RGB').filter(ImageFilter.GaussianBlur(radius=10))
    m_img = np.asarray(m_img) / 255.0
    img_np = np.asarray(expand_img.convert('RGB')) / 255.0
    ours_np = np.asarray(result) / 255.0
    ours_np = ours_np * m_img + (1 - m_img) * img_np
    
    result_paste = Image.fromarray(np.uint8(ours_np * 255))
    return np.array(result_paste)

