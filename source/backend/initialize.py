from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import os 
import io
import uvicorn
import sys 
sys.path.append('/mmlabworkspace/Students/visedit/VisualEditing/source')
from cores.interpreter import Interpreter
from cores.generator import OpenAIGenerator, GeminiGenerator
from utils.config_manager import ConfigManager
from utils.read_txt import read_txt
from fastapi import FastAPI, Form, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import traceback
from PIL import Image
import csv
import base64 
import re
import json
from natsort import natsorted
from fastapi import File, UploadFile, Form, HTTPException
from fastapi.param_functions import File
import asyncio
from copy import deepcopy
from fastapi.responses import FileResponse
OPENAI_API_KEY = 'YOUR_API_KEY'
GEMINI_API_KEY = 'YOUR_API_KEY'
CONFIG_FILE_PATH = "config.yaml"
config_manager = ConfigManager(CONFIG_FILE_PATH)
OPENAI_MODEL_NAME = config_manager.get("openai_model_name")
GEMINI_MODEL_NAME = config_manager.get("gemini_model_name")
FEWSHOT_FILE_PATH = config_manager.get("fewshot_file_path")
INIT_VARNAME = config_manager.get("initial_varname")
FEWSHOT_PROMPT = read_txt(FEWSHOT_FILE_PATH)
# generator = OpenAIGenerator(model=OPENAI_MODEL_NAME, api_key=OPENAI_API_KEY)
generator = GeminiGenerator(model_name=GEMINI_MODEL_NAME, api_key=GEMINI_API_KEY)
generator.load_prefix(FEWSHOT_FILE_PATH)
interpreter = Interpreter(init_varname=INIT_VARNAME)

class ImageData(BaseModel):
    index: int
    base64_string: str

class ProcessRequest(BaseModel):
    instruction: str
    images: List[ImageData]
    keep_track: bool 
    
class ImageState:
    original_images = None
    work_images = None

    @classmethod
    def reset_images(cls, image_data_list):
        cls.original_images = image_data_list
        cls.work_images = deepcopy(image_data_list)

    @classmethod
    def should_reset(cls, current_list, keep_track):
        if not keep_track:
            return True
        if cls.original_images is None or not np.array_equal(current_list, cls.original_images):
            return True
        return False
    
def load_images(image_data_list: List[ImageData]):
    images = []
    for image_data in image_data_list:  
        base64_data = image_data.base64_string.split(',')[1]
        image_bytes = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_bytes))
        images.append(np.array(image))
    return images

def is_numpy_array(obj):
    return isinstance(obj, np.ndarray)

def get_pil_image(image: np.ndarray):
    pil_image = Image.fromarray(image)
    return pil_image

def encode_image_to_base64(image):
    buffered = io.BytesIO()
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def decode_base64_to_image(base64_string):
    img_data = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(img_data))
    return np.array(img)

def encode_video_to_base64(video_path):
    with open(video_path, "rb") as video_file:
        video_content = video_file.read()
    return base64.b64encode(video_content).decode('utf-8')

def parse_chosen_images(chosen_images_str, total_images):
    chosen_indices = []
    img_strs = chosen_images_str.strip().split(',')
    for img_str in img_strs:
        img_str = img_str.strip()
        if img_str.isdigit():
            chosen_indices.append(int(img_str))
        elif re.match(r'-\d+', img_str):
            negative_index = int(img_str)
            positive_index = total_images + negative_index
            if 0 <= positive_index < total_images:
                chosen_indices.append(positive_index)
        elif img_str == 'all':
            chosen_indices.append('all')
        else:
            return None
    return chosen_indices

async def edit_request(instruction: str, uploaded_images: list, max_retries=2):
    result = None 
    for _ in range(max_retries):
        try:
            identity = deepcopy(uploaded_images)
            total_images = len(uploaded_images)
            program = generator.generate(instruction)
            program = re.sub(r'^.*```.*$', '', program, flags=re.MULTILINE).strip()
            print(program)
            detail = program.strip().split('\n')
            chosen_images = detail.pop(0)                                   
            chosen_images = chosen_images[chosen_images.find(":") + 2:]    
            chosen_indices = parse_chosen_images(chosen_images, total_images)
            print(f'This is the chosen indices: {chosen_indices}')

            
            if detail[0]=="": detail.pop(0)
            if detail[0].find("```") != -1: detail.pop(0)
            if detail[-1].find("```") != -1: detail.pop()
            
            # This part is designed for EDITING IMAGE
            if detail[1].find("video") == -1:
                for selected_image in chosen_indices:
                    if detail[0].startswith('Program'):
                        detail.pop(0)
                        program = ""
                        while len(detail) > 0 and (not detail[0].startswith('Program')):
                            program += detail.pop(0) + '\n'
                        
                        if selected_image == 'all':
                            for i in range(len(uploaded_images)):
                                image = uploaded_images[i]
                                image = np.array(image)
                                result = interpreter.editimage(image, program)
                                interpreter.reset()
                                print(result.edit_status)
                                uploaded_images[i] = get_pil_image(result.image)
                        else:
                            image = uploaded_images[selected_image]
                            image = np.array(image)
                            result = interpreter.editimage(image, program)
                            interpreter.reset()
                            print(result.edit_status)
                            uploaded_images[selected_image] = get_pil_image(result.image)
                
                pil_uploaded_images = [get_pil_image(img) if isinstance(img, np.ndarray) else img for img in uploaded_images]
                base64_uploaded_images = [encode_image_to_base64(img) for img in pil_uploaded_images]
                different_indices = [i for i, (img1, img2) in enumerate(zip(uploaded_images, identity)) if not np.array_equal(img1, img2)]
                print(f"Different indices: {different_indices}")
                pil_edited_images = [get_pil_image(uploaded_images[i]) if isinstance(uploaded_images[i], np.ndarray) else uploaded_images[i] for i in different_indices]
                base64_edited_images = [encode_image_to_base64(img) for img in pil_edited_images]
                result = {
                    "type": "image",
                    "base64_uploaded_images": base64_uploaded_images,
                    "different_indices": different_indices
                }
                if different_indices:
                    break
                else:
                    print("No different indices, retrying...")
                    
            else:
                detail.pop(0)
                program = ""
                while len(detail) > 0:
                    program += detail.pop(0) + '\n'
                video_path = interpreter.generate_video(chosen_indices, uploaded_images, program)
                if video_path:
                    video_base64 = encode_video_to_base64(video_path)
                    result = {
                    "type": "video",
                    "data": video_base64  
                    }
                    break  
                        
        except Exception as e:
            print(f"Retry due to error: {e}")
            await asyncio.sleep(1)  
            continue
    if result is not None:
        return result
    
# def edit(selected_image, program, image_list):
#     if selected_image == 'all':
#         for i in range(len(image_list)):
#             image = image_list[i]
#             image = np.array(image)
#             result = interpreter.editimage(image, program)
#             interpreter.reset()
#             print(result.edit_status)
#             image_list[i] = get_pil_image(result.image)
#     else:
#         image = image_list[selected_image]
#         image = np.array(image)
#         result = interpreter.editimage(image, program)
#         interpreter.reset()
#         print(result.edit_status)
#         image_list[selected_image] = get_pil_image(result.image)