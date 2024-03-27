import os, sys
sys.path.append(os.path.abspath(os.getcwd()))

from typing import Literal
from .base_module import MaskApplier
from source.cores.image_record import ImageRecord
from source.modules.engines.edition.edit import call_edit_image_api
import base64
import requests
import numpy as np
from PIL import Image
import io

class Replacer(MaskApplier):

    def __init__(self, image_record: ImageRecord) -> None:
        super().__init__(image_record)

    def replace(self, instruction: str) -> ImageRecord:
        result = self.image_record.create_next()
        original_image_array = result.image
        replaced_image = call_edit_image_api(original_image_array, instruction)
        return self.apply_mask(result, None, replaced_image)

            
        
