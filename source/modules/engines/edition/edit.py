import os, sys
sys.path.append(os.path.abspath(os.getcwd()))
from typing import Literal
import base64
import requests
import numpy as np
from PIL import Image
import io

def call_edit_image_api(image_array: np.array, instruction_text: str) -> np.array:
    image = Image.fromarray(image_array)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    url = "http://localhost:3333/edit_image"
    
    data = {
        "image": img_str,
        "instruction": instruction_text
    }
    
    response = requests.post(url, json=data, timeout=300)
    if response.status_code == 200:
        edited_img_data = base64.b64decode(response.json())
        edited_img = Image.open(io.BytesIO(edited_img_data))
        edited_image_array = np.array(edited_img)
        return edited_image_array
    else:
        raise Exception(f"API call failed with status code {response.status_code}")