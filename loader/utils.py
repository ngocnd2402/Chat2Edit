import PIL
import cv2 as cv
import numpy as np

import torch
from torchvision.ops import box_convert
from torchvision import transforms as T

from typing import Union

def generate_masks_with_grounding(image_source, boxes):
    h, w, _ = image_source.shape
    boxes_unnorm = boxes * torch.Tensor([w, h, w, h])
    boxes_xyxy = box_convert(boxes=boxes_unnorm, in_fmt="cxcywh", out_fmt="xyxy").numpy()
    mask = np.zeros_like(image_source)
    for box in boxes_xyxy:
        x0, y0, x1, y1 = box
        mask[int(y0):int(y1), int(x0):int(x1), :] = 255
    return mask

def show_mask(mask, image, random_color=True):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.8])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.cpu().reshape(h, w, 1) * color.reshape(1, 1, -1)
    
    annotated_frame_pil = PIL.Image.fromarray(image).convert("RGBA")
    mask_image_pil = PIL.Image.fromarray((mask_image.cpu().numpy() * 255).astype(np.uint8)).convert("RGBA")

    return np.array(PIL.Image.alpha_composite(annotated_frame_pil, mask_image_pil))

def make_inpaint_condition(image, image_mask):
    image = np.array(image.convert("RGB")).astype(np.float32) / 255.0
    image_mask = np.array(image_mask.convert("L")).astype(np.float32) / 255.0

    assert image.shape[0:1] == image_mask.shape[0:1], "image and image_mask must have the same image size"
    image[image_mask > 0.5] = -1.0  # set as masked pixel
    image = np.expand_dims(image, 0).transpose(0, 3, 1, 2)
    image = torch.from_numpy(image)
    return image

def rescale_on_range(image: Union[PIL.Image.Image, np.ndarray, torch.Tensor], return_type:str='np', min_range:int = 768):
    assert return_type in ['pl', 'pt', 'np'], f"return_type only support 'pl' for PIL.Image.Image, 'np' for np.ndarray and 'pt' for torch.tensor, get {return_type}"
    if torch.is_tensor(image):
        image = image.permute(1,2,0).cpu().numpy()
    
    elif isinstance(image, PIL.Image.Image):
        image = np.array(image)

    ever_change = False
    image_width, image_height, _ = image.shape

    if (min(image_height, image_width) > min_range) or (max(image_height, image_width) < min_range):
        scale_factor = min(min_range / image_height, min_range / image_width)
        image_width, image_height = int(image_width * scale_factor), int(image_height * scale_factor)
        ever_change = True

    remainder_by_height = image_height % 8
    if remainder_by_height != 0:
        image_height += (8 - remainder_by_height)
        ever_change = True

    remainder_by_width = image_width % 8
    if remainder_by_width != 0:
        image_width += (8 - remainder_by_width)
        ever_change =True
        
    if ever_change:
        image = cv.resize(src=image, dsize=(image_height, image_width))
    
    if return_type == 'pl':
        image = PIL.Image.fromarray(image)
    
    elif return_type == 'pt':
        # image = np.transpose(image, (3,0,1))
        image = T.ToTensor()(image)

    return image


class TimeMeter:
    def __init__(self,):
        self.total_det_time = 0
        self.total_segment_time = 0
        self.total_editting_time = 0
    
    def update_det(self,val):
        self.total_det_time += val

    def update_seg(self,val):
        self.total_segment_time += val
    
    def update_diff(self,val):
        self.total_editting_time += val
    
    def get_total_info(self,):
        total_time = self.total_det_time + self.total_segment_time + self.total_editting_time
        return_info = f"Detection takes {self.total_det_time:.3f}s, \
                        Segmentation takes {self.total_segment_time:.3f}s, \
                        Editting takes {self.total_editting_time:.3f}s \
                        Total: {total_time:.3f}s"
        return return_info
    
# def inpaint(image: np.array, instruction: str, device: str = 'cuda'):
#     guidance_scale = 9.5
#     generator = torch.Generator(device="cuda").manual_seed(-1)
#     original_size = image.shape[:2]  
#     image_pil = Image.fromarray(image).resize((512, 512))
#     mask_image_pil = segment(image, instruction).resize((512, 512))
#     images = inpainter(
#         prompt=instruction,
#         image=image_pil,
#         mask_image=mask_image_pil,
#         guidance_scale=guidance_scale,
#         generator=generator,
#         num_inference_steps=70,
#     ).images
#     img_res = images[0]
#     img_res = img_res.resize(original_size[::-1], Image.LANCZOS)  
#     inpainted_image_np = np.array(img_res)
#     return inpainted_image_np

# def create_transparent_mask(image: np.array, instruction: str):
#     image_source = Image.fromarray(image)
#     image_source = src.rescale_on_range(image_source, return_type='np')
#     segmenter.set_image(image_source)
#     boxes_xyxy, logits, phrases = detect(image, instruction)
#     transformed_boxes = segmenter.transform.apply_boxes_torch(boxes_xyxy, image_source.shape[:2]).to(DEVICE)
#     masks, _, _ = segmenter.predict_torch(
#         point_coords = None,
#         point_labels = None,
#         boxes = transformed_boxes,
#         multimask_output = False,
#     )
#     final_mask = torch.sum(masks, dim=0,dtype=torch.bool)
#     image_mask = final_mask[0].cpu().numpy() 
#     image_mask = image_mask.astype(np.uint8)
#     image_mask *= 255
#     kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(15,15))
#     image_mask = cv.morphologyEx(image_mask, cv.MORPH_OPEN, kernel)
#     image_mask = cv.morphologyEx(image_mask, cv.MORPH_OPEN, kernel)
#     height, width = image_mask.shape
#     transparent_img = np.zeros((height, width, 4), dtype=np.uint8)
#     for i in range(3):  
#         transparent_img[:, :, i] = image_mask
#     transparent_img[:, :, 3] = np.where(image_mask > 0, 255, 0)  # Alpha channel
#     output_image = Image.fromarray(transparent_img)
#     output_image.save("/mmlabworkspace/Students/visedit/VisualEditing/deepfillv2/examples/inpaint/masked_image_transparent.png", "PNG")
#     return output_image