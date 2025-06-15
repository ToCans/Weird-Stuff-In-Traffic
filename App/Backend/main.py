"""main.py"""
# General Library Imports
import re
import os

# Backend Library Imports
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

# AI Related Imports
from ultralytics import YOLO
from diffusers import StableDiffusionXLInpaintPipeline, DPMSolverMultistepScheduler
from detectron2.engine import DefaultPredictor
import transformers
import torch

# Schema Imports
from schemas.images import DetectionRequest, DetectionResponse, ImageGenerationPrompt, GeneratedImages

# Model Config Imports
from models.configurations import detectron_cfg

# Function Imports
from services import states
from services.image_detection import detect
from services.image_generation import generate


# Setting Correct Paths
current_directory = os.getcwd()
path_to_base_directory = re.search(rf"(.*?){"Weird-Stuff-In-Traffic"}", current_directory).group(1)

# Model Paths
street_detection_model_path = "Weird-Stuff-In-Traffic/App/Backend/models"
full_street_detection_detection_model_path = path_to_base_directory + street_detection_model_path + "/streetseg_256_auto.pt"

# Context Manager
@asynccontextmanager
async def lifespan(_):
    """App Lifespan."""
    print("Loading models...")
    states.DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    states.BACKEND_LOCK = asyncio.Lock()
    states.GENERATION_MODEL = StableDiffusionXLInpaintPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0",torch_dtype=torch.float16, variant="fp16", safety_checker=None).to(states.DEVICE)
    states.GENERATION_MODEL.scheduler = DPMSolverMultistepScheduler.from_config(states.GENERATION_MODEL.scheduler.config)
    states.WEIRD_DETECTION_MODEL = DefaultPredictor(detectron_cfg)
    states.STREET_DETECTION_MODEL = YOLO(full_street_detection_detection_model_path).to(states.DEVICE)
    states.DETECTION_DESCRIPTION_PROCESSOR = transformers.Qwen2VLProcessor.from_pretrained("Qwen/Qwen2-VL-7B-Instruct", use_fast=True)
    states.DETECTION_DESCRIPTION_MODEL = transformers.Qwen2VLForConditionalGeneration.from_pretrained("Qwen/Qwen2-VL-7B-Instruct", torch_dtype=torch.float16).to(states.DEVICE)
    print(f"Using {states.DEVICE}.")
    print("Models loaded.")
    yield
    states.DEVICE = None
    states.GENERATION_MODEL = None
    states.WEIRD_DETECTION_MODEL = None
    states.STREET_DETECTION_MODEL = None
    states.DETECTION_DESCRIPTION_MODEL = None
    states.DETECTION_DESCRIPTION_PROCESSOR = None
    states.BACKEND_LOCK = None
    print("Models shut down.")

# Defining App
app = FastAPI(lifespan=lifespan)

# Routes
@app.post("/detect", response_model=DetectionResponse)
async def detect_endpoint(req: DetectionRequest):
    """Endpoint for detecting weird objects in an image."""
    return await detect(req)

@app.post("/generate", response_model=GeneratedImages)
async def generate_endpoint(req: ImageGenerationPrompt):
    """Endpoint for detecting weird objects in an image."""
    return await generate(req)

# Main Running Area
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
