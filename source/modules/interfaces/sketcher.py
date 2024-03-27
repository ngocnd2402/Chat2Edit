import os, sys
sys.path.append(os.path.abspath(os.getcwd()))
from typing import Literal
from .base_module import MaskApplier
from source.cores.image_record import ImageRecord
from source.modules.engines.basic.process_image import img_to_sketch

class Sketcher(MaskApplier):

    def __init__(self, image_record: ImageRecord) -> None:
        super().__init__(image_record)

    def sketch(self, target: str | None) -> ImageRecord:
        result = self.image_record.create_next()
        sketch_img = img_to_sketch(result.image)
        return self.apply_mask(result, target, sketch_img)
