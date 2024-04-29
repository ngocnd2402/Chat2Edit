from init import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.post("/gen_image")
# async def gen_images(request_data: GeneratingImageRequest):
#     generated_image = np.array(generate(request_data.instruction))
#     buffered = io.BytesIO()
#     img = Image.fromarray(generated_image)
#     img.save(buffered, format="JPEG")
#     encoded_string = base64.b64encode(buffered.getvalue()).decode()
#     return encoded_string

@app.post("/edit_image")
async def edit_images(request_data: ImageManipulationRequest):
    image_data = base64.b64decode(request_data.image)
    image = Image.open(io.BytesIO(image_data))
    image_array = np.array(image)
    edited_image = edit(image_array, request_data.instruction)
    if not isinstance(edited_image, np.ndarray):
        edited_image = np.array(edited_image)
    buffered = io.BytesIO()
    img = Image.fromarray(edited_image)
    img.save(buffered, format="JPEG")
    encoded_string = base64.b64encode(buffered.getvalue()).decode()
    return encoded_string

@app.post("/detect_object")
async def detect_objects(request_data: ImageManipulationRequest):
    image_data = base64.b64decode(request_data.image)
    image = Image.open(io.BytesIO(image_data))
    image_array = np.array(image)
    boxes = detect(image_array, request_data.instruction)
    boxes_list = boxes.tolist()
    for box in boxes_list:
        x1, y1, x2, y2 = box
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        cv.rectangle(image_array, (x1, y1), (x2, y2), (255, 0, 0), 4)
    buffered = io.BytesIO()
    img = Image.fromarray(image_array)
    img.save(buffered, format="JPEG")
    encoded_string = base64.b64encode(buffered.getvalue()).decode()
    return encoded_string

@app.post("/segment_object")
async def segment_objects(request_data: ImageManipulationRequest):
    image_data = base64.b64decode(request_data.image)
    image = Image.open(io.BytesIO(image_data))
    image_array = np.array(image)
    image_mask = segment(image_array, request_data.instruction)
    image_mask = np.array(image_mask)
    if len(image_mask.shape) == 3: 
        image_mask = image_mask[:, :, 0] 
    highlight_color = np.array([255, 0, 255], dtype=np.uint8) 
    color_mask = np.zeros_like(image_array, dtype=np.uint8)
    color_mask[image_mask == 255] = highlight_color  
    output_image = np.where(color_mask, color_mask, image_array)
    img_with_mask = Image.fromarray(output_image)
    buffered = io.BytesIO()
    img_with_mask.save(buffered, format="JPEG")
    encoded_string = base64.b64encode(buffered.getvalue()).decode()
    return encoded_string

@app.post("/delete_object")
async def delete_objects(request_data: ImageObjectRemovalRequest):
    image_data = base64.b64decode(request_data.image)
    image = Image.open(io.BytesIO(image_data))
    image_array = np.array(image)
    img_removed_object = delete(image_array, request_data.instruction,  request_data.negative, device=DEVICE)
    buffered = io.BytesIO()
    img_pil = Image.fromarray(img_removed_object)
    img_pil.save(buffered, format="JPEG")
    result_base64 = base64.b64encode(buffered.getvalue()).decode()
    return result_base64

@app.post("/expand_image")
async def expand_images(request_data: ExpandRequest):
    image_data = base64.b64decode(request_data.image)
    vertical = request_data.vertical_expansion_ratio
    horizon = request_data.horizontal_expansion_ratio
    image = Image.open(io.BytesIO(image_data))
    image_array = np.array(image)
    img_expand = expand(image_array, vertical, horizon)
    buffered = io.BytesIO()
    img_pil = Image.fromarray(img_expand)
    img_pil.save(buffered, format="JPEG")
    result_base64 = base64.b64encode(buffered.getvalue()).decode()
    return result_base64

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3333)
