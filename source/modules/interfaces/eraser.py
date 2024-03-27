import os, sys
sys.path.append(os.path.abspath(os.getcwd()))

from typing import Literal
from .base_module import MaskApplier
from source.cores.image_record import ImageRecord
from source.modules.engines.erasion.erase import call_erase_object_api
import base64
import requests
import numpy as np
from PIL import Image
import io

class Eraser(MaskApplier):

    def __init__(self, image_record: ImageRecord) -> None:
        super().__init__(image_record)

    def erase(self, instruction: str, negative: str) -> ImageRecord:
        result = self.image_record.create_next()
        original_image_array = result.image
        delected_image = call_erase_object_api(original_image_array, instruction, negative)
        return self.apply_mask(result, None, delected_image)

            
        
