import os, sys
sys.path.append('/mmlabworkspace/Students/visedit/VisualEditing/source')

from typing import Literal
import base64
import requests
import numpy as np
from PIL import Image
import io

def call_detect_object_api(image_array: np.array, instruction: str) -> np.array:
    image = Image.fromarray(image_array)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    url = "http://localhost:3333/detect_object"
    
    data = {
        "image": img_str,
        "instruction": instruction
    }
    
    response = requests.post(url, json=data, timeout=300)
    if response.status_code == 200:
        detected_img_data = base64.b64decode(response.json())
        detected_img = Image.open(io.BytesIO(detected_img_data))
        detected_image_array = np.array(detected_img)
        return detected_image_array
    else:
        raise Exception(f"API call failed with status code {response.status_code}")