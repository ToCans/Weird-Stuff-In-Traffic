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
import transformers
import torch

# Schema Imports
from schemas.images import DetectionRequest, DetectionResponse

# Function Imports
from services import states
from services.image_detection import detect


# Setting Correct Paths
current_directory = os.getcwd()
path_to_base_directory = re.search(rf"(.*?){"Weird-Stuff-In-Traffic"}", current_directory).group(1)

# Model Paths
best_detection_model_path = "Weird-Stuff-In-Traffic/Models/Segmentation-Detection/yolo/coco8_clean/fine_tuned_model/experiment"
full_detection_model_path = path_to_base_directory + best_detection_model_path + "/weights/best.pt"

# Context Manager
@asynccontextmanager
async def lifespan(_):
    """App Lifespan."""
    print("Loading models...")
    states.MODEL_LOCK = asyncio.Lock()
    #states.GENERATION_MODEL = "GenerationModelLoaded"
    states.DETECTION_MODEL = YOLO(full_detection_model_path)
    states.DETECTION_DESCRIPTION_PROCESSOR = transformers.Qwen2VLProcessor.from_pretrained("Qwen/Qwen2-VL-2B-Instruct", use_fast=True)
    states.DETECTION_DESCRIPTION_MODEL = transformers.Qwen2VLForConditionalGeneration.from_pretrained("Qwen/Qwen2-VL-2B-Instruct", torch_dtype=torch.float16, device_map="auto")
    states.DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using {states.DEVICE}.")
    print("Models loaded.")
    yield
    states.DETECTION_MODEL = None
    states.DETECTION_DESCRIPTION_MODEL = None
    states.DETECTION_DESCRIPTION_PROCESSOR = None
    states.DEVICE = None
    states.MODEL_LOCK = None
    print("Models shut down.")

# Defining App
app = FastAPI(lifespan=lifespan)

# Routes
@app.post("/detect", response_model=DetectionResponse)
async def detect_endpoint(req: DetectionRequest):
    """Endpoint for detecting weird objects in an image."""
    return await detect(req)

# Main Running Area
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
