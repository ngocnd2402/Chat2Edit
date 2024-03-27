import os, sys
sys.path.append(os.path.abspath(os.getcwd()))

import numpy as np
from typing import Callable
from source.cores.image_record import ImageRecord, EditStatus
from source.modules.engines.basic.process_image import forebackground_segment
# from src.modules.engines.huggingface.segmentation import face_segment, cloth_segment, general_segment   #Hiện tại đang chỉ dùng foreground / background segmentation


FACE_TARGETS = ["lips", "eyes", "skin"]
FOREBACKGROUND_TARGETS = ["foreground", "background"]
CLOTHES_TARGETS = ["pants", "upper-clothes", "face", "hair"]


class Module:

    def __init__(self, image_record: ImageRecord) -> None:
        self.image_record = image_record


    def segment(self, image_record: ImageRecord, target: str) -> None:
        if target not in image_record.masks:
            masks = None
            if target in FOREBACKGROUND_TARGETS: masks = forebackground_segment(image_record.image)
            # elif target in FACE_TARGETS: masks = face_segment(image_record.image)
            # elif target in CLOTHES_TARGETS: masks = cloth_segment(image_record.image)
            # else: masks = general_segment(image_record.image)
        
            for obj, mask in masks.items():
                if obj not in image_record.masks:
                    image_record.masks[obj] = mask

    
    def mask_to_bbox(self, mask: np.ndarray) -> np.ndarray:
        non_zero_coords = np.column_stack(np.where(mask > 0))
        x_min, y_min = np.min(non_zero_coords, axis=0)
        x_max, y_max = np.max(non_zero_coords, axis=0)
        return np.array([x_min, y_min, x_max, y_max])
                
    


class MaskApplier(Module):

    def __init__(self, image_record: ImageRecord) -> None:
        super().__init__(image_record)


    def apply_mask(self, image_record: ImageRecord, target: str, transformed_image: np.ndarray) -> ImageRecord:
        if target is None:
            image_record.image = transformed_image
            image_record.edit_status = EditStatus.SUCCESS
            return image_record

        self.segment(image_record, target)
            
        if target in image_record.masks:
            target_mask = image_record.masks[target]
            image_record.image[target_mask == 255] = transformed_image[target_mask == 255]
            image_record.edit_status = EditStatus.SUCCESS
        else: 
            image_record.edit_status = EditStatus.TARGET_NOT_FOUND
        
        return image_record



class SpaceTransformer(Module):
    
    def __init__(self, image_record: ImageRecord) -> None:
        super().__init__(image_record)


    def transform(self, image_record: ImageRecord, func: Callable, *args, **kwargs) -> ImageRecord:
        image_record.image = func(image_record.image, *args, **kwargs)

        for obj, mask in image_record.masks.items():
            image_record.masks[obj] = func(mask, *args, **kwargs)

        image_record.edit_status = EditStatus.SUCCESS
        return image_record