import os, sys
sys.path.append(os.path.abspath(os.getcwd()))
from typing import Literal
from .base_module import MaskApplier
from source.cores.image_record import ImageRecord
from source.modules.engines.basic.process_image import edge_sobel, edge_canny



class Edge_Detect(MaskApplier):

    def __init__(self, image_record: ImageRecord) -> None:
        super().__init__(image_record)


    def edge(self, method: Literal["sobel", "canny"] | None, target: str | None) -> ImageRecord:
        result = self.image_record.create_next()
        if method is None: method = 'sobel'
        if method == 'sobel': edge_image = edge_sobel(result.image)
        elif method == 'canny': edge_image = edge_canny(result.image)
        else: raise ValueError(f"Unsupported method \"{method}\" for edge detection module")
        return self.apply_mask(result, target, edge_image)

            
        
