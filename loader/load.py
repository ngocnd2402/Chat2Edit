import torch
from GroundingDINO.groundingdino.models import build_model
from GroundingDINO.groundingdino.util.slconfig import SLConfig
from GroundingDINO.groundingdino.util.utils import clean_state_dict
from huggingface_hub import hf_hub_download
from SAM.segment_anything import build_sam, SamPredictor
from diffusers import UNet2DConditionModel, StableDiffusionPipeline, StableDiffusionInpaintPipeline, StableDiffusionControlNetInpaintPipeline, ControlNetModel, PNDMScheduler, DDIMScheduler, UniPCMultistepScheduler, DPMSolverMultistepScheduler, StableDiffusionXLInpaintPipeline, DPMSolverSinglestepScheduler
from controlnet_aux import HEDdetector, OpenposeDetector
from transformers import DPTFeatureExtractor, DPTForDepthEstimation
from PowerPaint.utils.utils import TokenizerWrapper, add_tokens
from PowerPaint.pipeline.pipeline_PowerPaint import StableDiffusionInpaintPipeline as Pipeline
from PowerPaint.pipeline.pipeline_PowerPaint_ControlNet import StableDiffusionControlNetInpaintPipeline as controlnetPipeline
from PIL import Image, ImageFilter
from diffusers.pipelines.controlnet.pipeline_controlnet import ControlNetModel
from safetensors.torch import load_model

def getGroundingDINO(device:str, filename:str, ckpt_config_filename:str, repo_id:str = "ShilongLiu/GroundingDINO"):
    cache_config_file = hf_hub_download(repo_id=repo_id, filename=ckpt_config_filename)

    args = SLConfig.fromfile(cache_config_file) 
    model = build_model(args)
    args.device = device

    cache_file = hf_hub_download(repo_id=repo_id, filename=filename)
    checkpoint = torch.load(cache_file, map_location='cpu')
    log = model.load_state_dict(clean_state_dict(checkpoint['model']), strict=False)
    print("Model loaded from {} \n => {}".format(cache_file, log))
    _ = model.eval()
    return model 

def getSAM(ckpt:str, device:str) -> SamPredictor:
    '''
    Load SAM (Segment Anything)

    Argument:
        ckpt (str) ckpt path to SAM
        device (str) which device to load model ('cpu' or 'cuda')
    '''
    sam = build_sam(checkpoint=ckpt)
    sam.to(device=device)
    sam_predictor = SamPredictor(sam)

    return sam_predictor

def getControlNet(stable_diffusion_name:str, controlnet_name: str, device:str):
    '''
    Load ControlNET condition for Stable Diffusion

    Argument:
        stable_diffusion_name (str) Huggingface Stable Diffusion name
        controlnet_name (str) Huggingface ControlNet condiion name
        device (str) which device to load model ('cpu' or 'cuda')
    '''
    controlnet = ControlNetModel.from_pretrained(controlnet_name, torch_dtype=torch.float16)
    pipe = StableDiffusionControlNetInpaintPipeline.from_pretrained(stable_diffusion_name, controlnet=controlnet, torch_dtype=torch.float16, safety_checker=None)
    # scheduler = DPMSolverSinglestepScheduler.from_config(pipe.scheduler.config)
    pipe.enable_model_cpu_offload()
    pipe.enable_attention_slicing()
    pipe.to(device)

    return pipe

def getDiffusers(model_id:str, device:str):
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    # pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.enable_attention_slicing()
    pipe = pipe.to(device)
    return pipe

def getPowerPaint(stable_inpaint_name:str, stable_diffusion_name:str, device:str):
    pipe = Pipeline.from_pretrained(
        stable_inpaint_name,
        torch_dtype=torch.float16).to(device)
    pipe.tokenizer = TokenizerWrapper(
        from_pretrained=stable_diffusion_name,
        subfolder='tokenizer',
        revision=None)
    add_tokens(
        tokenizer=pipe.tokenizer,
        text_encoder=pipe.text_encoder,
        placeholder_tokens=['P_ctxt', 'P_shape', 'P_obj'],
        initialize_tokens=['a', 'a', 'a'],
        num_vectors_per_token=10)
    load_model(pipe.unet, "PowerPaint/models/unet/unet.safetensors")
    load_model(pipe.text_encoder, "PowerPaint/models/text_encoder/text_encoder.safetensors")
    return pipe