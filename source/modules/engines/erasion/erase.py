import os, sys
sys.path.append(os.path.abspath(os.getcwd()))
from typing import Literal
import base64
import requests
import numpy as np
from PIL import Image
import io

def call_erase_object_api(image_array: np.array, instruction: str, negative: str) -> np.array:
    image = Image.fromarray(image_array)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    url = "http://localhost:3333/delete_object"
    
    data = {
        "image": img_str,
        "instruction": instruction,
        "negative": negative
    }
    
    response = requests.post(url, json=data, timeout=300)
    if response.status_code == 200:
        segmented_img_data = base64.b64decode(response.json())
        segmented_img = Image.open(io.BytesIO(segmented_img_data))
        segmented_image_array = np.array(segmented_img)
        return segmented_image_array
    else:
        raise Exception(f"API call failed with status code {response.status_code}")