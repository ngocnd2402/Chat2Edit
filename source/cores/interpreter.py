import os, sys
sys.path.append(os.path.abspath(os.getcwd()))
from typing import Any, Dict, List
import re
import numpy as np
from .image_record import ImageRecord
from source.modules.interfaces.scaler import Scaler
from source.modules.interfaces.converter import Converter
from source.modules.interfaces.rotator import Rotator
from source.modules.interfaces.flipper import Flipper
from source.modules.interfaces.zoomer import Zoomer
from source.modules.interfaces.denoise import Denoiser
from source.modules.interfaces.edge import Edge_Detect
from source.modules.interfaces.replacer import Replacer
from source.modules.interfaces.detecter import Detecter
from source.modules.interfaces.segmenter import Segmenter
from source.modules.interfaces.vidoer import VideoGenerator
from source.modules.interfaces.equalizer import Equalizer
from source.modules.interfaces.eraser import Eraser
from source.utils.checktype import is_int_format, is_float_format, is_string_format


class Interpreter:
    def __init__(self, init_varname: str) -> None:
        self.context = {}                       
        self.init_varname = init_varname        

    def editimage(self, image: np.ndarray, program) -> ImageRecord:
        image_record = ImageRecord(image)
        self.context[self.init_varname] = image_record
        steps = self.parse_program(program)
        for step in steps:
            varname, module, args_dict = self.parse_step(step)
            self.context[varname] = self.call_module(module, args_dict)
        return self.result()

    def generate_video(self, selected_image, image, program):
        self.video = VideoGenerator(selected_image, image)
        steps = self.parse_program(program)
        for step in steps:
            varname, module, args_dict = self.parse_step(step)
            self.call_module_video(module, args_dict, selected_image)
        return self.video.output_path 

    # def call_module_video(self, module, args_dict, selected_image):
    #     if module == "videogen":
    #         arg_names = ["previous", "position", "effect"]
    #         prev, selected_image, effect = self.get_arg_values(args_dict, arg_names)
    #         try:
    #             selected_image = int(selected_image)
    #         except: pass
    #         if effect == "fade" or effect == "random": self.video.cross_fade(selected_image)
    #         elif effect == "slide_left": self.video.slide(selected_image, "left")
    #         elif effect == "slide_right": self.video.slide(selected_image, "right")
    #         elif effect == "slide_top": self.video.slide(selected_image, "top")
    #         elif effect == "slide_bottom": self.video.slide(selected_image, "bottom")
    #         else: raise ValueError("Unsupported effect \"{effect}\"")   

    def call_module_video(self, module, args_dict, selected_image):
        if module == "videogen":
            arg_names = ["previous", "position", "effect"]
            prev, selected_image, effect = self.get_arg_values(args_dict, arg_names)

            try:
                selected_image = int(selected_image)
            except:
                pass

            if effect == "fade" or effect == "random":
                self.video.cross_fade(selected_image)
            elif effect == "slide_left":
                self.video.slide(selected_image, "left")
            elif effect == "slide_right":
                self.video.slide(selected_image, "right")
            elif effect == "slide_top":
                self.video.slide(selected_image, "top")
            elif effect == "slide_bottom":
                self.video.slide(selected_image, "bottom")
            else:
                raise ValueError(f"Unsupported effect \"{effect}\"")   

        if module == "video_release":
            self.video.release()
            self.video.reset()

    def call_module(self, module: str, args_dict: dict) -> np.ndarray:
        if module == "scale":
            arg_names = ["image", "category", "factor", "target"]
            image, category, factor, target = self.get_arg_values(args_dict, arg_names)
            return Scaler(self.context[image]).scale(category, target, factor)
        
        if module == "convert":
            arg_names = ["image", "category", "target"]
            image, category, target = self.get_arg_values(args_dict, arg_names)
            return Converter(self.context[image]).convert(category, target)

        if module == "rotate":
            arg_names = ["image", "angle", "direction"]
            image, angle, direction = self.get_arg_values(args_dict, arg_names)
            return Rotator(self.context[image]).rotate(angle, direction)
        
        if module == "flip":
            arg_names = ["image", "direction"]
            image, direction = self.get_arg_values(args_dict, arg_names)
            return Flipper(self.context[image]).flip(direction)
        
        if module == "zoom":
            arg_names = ["image", "factor", "target"]
            image, factor, target = self.get_arg_values(args_dict, arg_names)
            return Zoomer(self.context[image]).zoom(factor, target) 
          
        if module == "denoise":
            arg_names = ["image", "method", "target"]
            image, method, target = self.get_arg_values(args_dict, arg_names)
            return Denoiser(self.context[image]).denoise(method, target)
        
        if module == "equalize_hist":
            arg_names = ["image", "target"]
            image, target = self.get_arg_values(args_dict, arg_names)
            return Equalizer(self.context[image]).equalize_hist(target)
          
        if module == "edge":
            arg_names = ["image", "method", "target"]
            image, method, target = self.get_arg_values(args_dict, arg_names)
            return Edge_Detect(self.context[image]).edge(method, target)

        if module == "replace":
            arg_names = ["image", "instruction"]
            image, instruction = self.get_arg_values(args_dict, arg_names)
            return Replacer(self.context[image]).replace(instruction)

        if module == "detect":
            arg_names = ["image", "instruction"]
            image, instruction = self.get_arg_values(args_dict, arg_names)
            return Detecter(self.context[image]).detect(instruction)

        if module == "segment":
            arg_names = ["image", "instruction"]
            image, instruction = self.get_arg_values(args_dict, arg_names)
            return Segmenter(self.context[image]).segment(instruction)
        
        if module == 'erase':
            arg_names = ["image", "instruction", "negative"]
            image, instruction, negative = self.get_arg_values(args_dict, arg_names)
            return Eraser(self.context[image]).erase(instruction, negative)   
          
        raise ValueError("Unsupported module \"{module}\"")

    def get_arg_values(sefl, args_dict: Dict[str, int | float | str], arg_names: List[str]) -> List[Any]:
        return [args_dict[arg_name] if arg_name in args_dict else None
                for arg_name in arg_names]

    def result(self) -> ImageRecord:
        return list(self.context.values())[-1]
    
    def reset(self) -> None:
        self.context = {}

    def format_step(self, step: str) -> str:
        return step.strip()
    
    def parse_module_args(self, tokens: list[str]) -> list:
        args_dict = {tokens[i]:tokens[i + 1] for i in range(0, len(tokens) - 1, 2)}

        for name, val in args_dict.items():
            if is_string_format(val): args_dict[name] = val[1:-1]
            elif is_float_format(val): args_dict[name] = float(val)
            elif is_int_format(val): args_dict[name] = int(val)
            else: args_dict[name] = val
        return args_dict

    def parse_step(self, line: str) -> list[str]:
        delimiter_chars = ",=()"
        tokens = re.split('[' + re.escape(delimiter_chars) + ']', line)[:-1]
        tokens = [token.strip() for token in tokens]
        args_dict = self.parse_module_args(tokens[2:])
        step_info = [tokens[0], tokens[1], args_dict]
        return step_info

    def parse_program(self, program: str) -> list[str]:
        program = program.strip()
        steps = program.split("\n")
        steps = [self.format_step(step) for step in steps if step != ""]
        return steps