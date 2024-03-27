from initialize import *

app = FastAPI()
app_state = ImageState()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_image_state():
    return app_state

@app.post("/process")
async def process_multiimage(request: ProcessRequest, state: ImageState = Depends(get_image_state)):
    instruction = request.instruction
    image_data_list = request.images
    current_list = load_images(image_data_list)
    flag = request.keep_track
    print(flag)

    if state.should_reset(current_list, flag):
        state.reset_images(current_list)
    result = await edit_request(instruction, state.work_images)

    if result["type"] == "image":
        state.work_images = [decode_base64_to_image(base64_str) for base64_str in result.get("base64_uploaded_images", [])]
        if 'different_indices' in result and result['different_indices']:
            different_images = [result["base64_uploaded_images"][i] for i in result['different_indices']]
            return {"result": different_images}
        else:
            return {"result": []} 
        
    elif result["type"] == "video":
        print(f'Release video')
        return {"result": result["data"]}
    else:
        return {"result": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2222)