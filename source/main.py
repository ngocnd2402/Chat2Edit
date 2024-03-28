#WARNING: This file is for Chat2Edit with the old version for fewshot_imagevideo_backup.txt
import os, sys
sys.path.append(os.path.abspath(os.getcwd()))

import streamlit as st
from PIL import Image
import numpy as np
# from io import BytesIO
from cores.interpreter import Interpreter
from cores.generator import OpenAIGenerator
from utils.config_manager import ConfigManager
from utils.read_txt import read_txt


CONFIG_FILE_PATH = "config.yaml"
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") 
OPENAI_API_KEY='xxxxx'

config_manager = ConfigManager(CONFIG_FILE_PATH)
OPENAI_MODEL_NAME = config_manager.get("openai_model_name")
FEWSHOT_FILE_PATH = config_manager.get("fewshot_file_path")
INIT_VARNAME = config_manager.get("initial_varname")
FEWSHOT_PROMPT = read_txt(FEWSHOT_FILE_PATH)

generator = OpenAIGenerator(model=OPENAI_MODEL_NAME, api_key=OPENAI_API_KEY)
interpreter = Interpreter(init_varname=INIT_VARNAME)


#NOTE: Process chỉ chứa 1 trong 2 hoạt động: edit image hoặc videogen

def process(instruction: str):
    # print('This is the prompt after replacing:   ', prompt)
    # print('\n\n\n\n')
    program = generator.generate(FEWSHOT_PROMPT, instruction)
    print('\nThis is the gpt output:\n', program)
    print('\n done \n')
    detail = program.strip().split('\n')
    chosen_images = detail.pop(0)                               #get the chosen images (first line)
    chosen_images = chosen_images[chosen_images.find(":")+2:]   #remove the word "Chosen images: "
    chosen_images = chosen_images.strip().split(',')
    print(chosen_images)

    for i in range(len(chosen_images)):
        chosen_images[i] = chosen_images[i].strip()
        if chosen_images[i] == 'all': pass
        else: chosen_images[i] = int(chosen_images[i])

    #This part is designed for editting image
    if detail[2].find("video") == -1:
        for selected_image in chosen_images:
            if detail[0].startswith('Instruction'): detail.pop(0)   
            if detail[0].startswith('Program'):
                detail.pop(0)
                program = ""
                #start to extract the program
                while len(detail) > 0 and (not detail[0].startswith('Instruction')):   #break condition
                    program += detail.pop(0) + '\n'
                edit(selected_image, program)    
        return 'editimage'
    else:
    #This part is for generating video
        if detail[0].startswith('Instruction'): detail.pop(0)
        if detail[0].startswith('Program'):
            detail.pop(0)
            program = ""
            #start to extract the program
            while len(detail) > 0:
                program += detail.pop(0) + '\n'
            
            if chosen_images == ['all']: chosen_images = [i for i in range(len(uploaded_images))]

            return interpreter.generate_video(chosen_images,uploaded_images,program)

def edit(selected_image, program):
    #This part is designed for editing image
    if selected_image == 'all':
        for i in range(len(uploaded_images)):
            image = uploaded_images[i]
            image = np.array(image)
            result = interpreter.editimage(image, program)
            interpreter.reset()
            print(result.edit_status)

            #change the image to the new one
            uploaded_images[i] = get_pil_image(result.image)


    else:
        image = uploaded_images[selected_image]
        image = np.array(image)
        result = interpreter.editimage(image, program)
        interpreter.reset()
        print(result.edit_status)

        #change the image to the new one
        uploaded_images[selected_image] = get_pil_image(result.image)
    #end part

@st.cache_data
def get_pil_image(image: np.ndarray):
    pil_image = Image.fromarray(image)
    return pil_image

# @st.cache_data
# def get_image_bytes(image: np.ndarray, format: str) -> BytesIO:
#     img_byte_array = BytesIO()
#     pil_image = get_pil_image(image)
#     pil_image.save(img_byte_array, format=format)
#     img_byte_array.seek(0)
#     return img_byte_array

def main():
    st.set_page_config(
        page_title="Chat2Edit",
        page_icon="hehe",
        layout="wide"
    )

    title_html = """<h1 style='text-align: center;'>CHAT2EDIT</h1>"""
    subtitle_html = """<h5 style='text-align: center;'>MMLAB - UIT - VNU HCM</h5>"""
    st.markdown(title_html, unsafe_allow_html=True)
    st.markdown(subtitle_html, unsafe_allow_html=True)
    
    global uploaded_images

    uploaded_images = st.file_uploader("Please upload the images here", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    if uploaded_images != []:

        #update session_state to catch new events
        # if 'uploaded_images' in st.session_state: del st.session_state.uploaded_images
        # st.session_state.uploaded_images = uploaded_images

        if 'uploaded_images' not in st.session_state:
            st.session_state.uploaded_images = uploaded_images

        #visualize the image
        num_images = len(uploaded_images)
        cols = 4
        rows = ((num_images - 1) // cols) + 1 #number of rows

        for row in range(rows):
            col = st.columns(cols)
            for j in range(cols):
                if row * cols + j < num_images:
                    image = Image.open(uploaded_images[row * cols + j])
                    uploaded_images[row * cols + j] = image                 #convert all element in uploaded_images from st.file_uploader to PIL image at the first time
                    col[j].image(image, use_column_width=True)
                    col[j].write("Image {}".format(row * cols + j))

        #show instruction box after uploading the images
        instruction = st.text_input("Please provide the instructions here")
        if st.button("Submit"):
            if instruction == "":
                st.warning("You must provide instructions before submitting!")
                return
            else:
                print('\nThis is the instruction:   ', instruction,'\n')

                #reload 'uploaded_images' from session state
                del uploaded_images
                uploaded_images = st.session_state.uploaded_images

                res = process(instruction)

                if res == 'editimage':
                    try:
                        del col_video
                    except: 
                        pass

                    #save the already_modified array of images
                    st.session_state.uploaded_images = uploaded_images    

                    if uploaded_images != []:
                        num_images = len(uploaded_images)
                        cols = 4
                        rows = ((num_images - 1) // cols) + 1 #number of rows
                        
                        #Show images
                        for row in range(rows):
                            col = st.columns(cols)
                            for j in range(cols):
                                if row * cols + j < num_images:
                                    image = uploaded_images[row * cols + j]
                                    col[j].image(image, use_column_width=True)
                                    col[j].write("Image {}".format(row * cols + j))

                else:  
                    #In this case, res is the video_name file
                    #Show result video
                    video_file = open(res, 'rb')
                    video_bytes = video_file.read()
                    col_video = st.columns(3)
                    col_video[0].video(video_bytes)
                    col_video[0].write("Result video") 

if __name__ == "__main__":
    main()
