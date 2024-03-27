import os, sys
sys.path.append(os.path.abspath(os.getcwd()))

from typing import Literal
from .base_module import MaskApplier
from source.cores.image_record import ImageRecord
from source.modules.engines.segmentation.segment import call_segment_object_api
import base64
import requests
import numpy as np
from PIL import Image
import io

class Segmenter(MaskApplier):

    def __init__(self, image_record: ImageRecord) -> None:
        super().__init__(image_record)

    def segment(self, query: str) -> ImageRecord:
        result = self.image_record.create_next()
        original_image_array = result.image
        segmented_image = call_segment_object_api(original_image_array, query)
        return self.apply_mask(result, None, segmented_image)

            
        
