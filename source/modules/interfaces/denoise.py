import os, sys
sys.path.append(os.path.abspath(os.getcwd()))

from typing import Literal
from .base_module import MaskApplier
from source.cores.image_record import ImageRecord
from source.modules.engines.basic.process_image import denoise_NL, denoise_gaussian



class Denoiser(MaskApplier):

    def __init__(self, image_record: ImageRecord) -> None:
        super().__init__(image_record)


    def denoise(self, method: Literal["non-local", "gaussian"] | None, target: str | None) -> ImageRecord:
        result = self.image_record.create_next()
        
        if method is None: method = 'non-local'
        if method == 'non-local': denoised_image = denoise_NL(result.image)
        elif method == 'gaussian': denoised_image = denoise_gaussian(result.image)
        else: raise ValueError(f"Unsupported method \"{method}\" for denoise module")
        return self.apply_mask(result, target, denoised_image)

            
        
