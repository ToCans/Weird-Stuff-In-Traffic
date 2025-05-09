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

# State Machine Import
from services import states

# Schema Imports
from schemas.images import ImageGenerationPrompt, DetectionRequest, DetectionResponse

# Function Imports
from services.image_handling import detect, generate


# Setting Correct Paths
# Directory Paths
current_directory = os.getcwd()
path_to_base_directory = re.search(rf"(.*?){"Weird-Stuff-In-Traffic"}", current_directory).group(1)

# Model Paths
best_detection_model_path = "Weird-Stuff-In-Traffic/Models/Segmentation-Detection/yolo/coco8_clean/fine_tuned_model/experiment"
full_pretrained_model_path = path_to_base_directory + best_detection_model_path + "/weights/best.pt"

# Setting  App
app = FastAPI()

# Encapsulate models in a dictionary
MODELS = {
    "PROMPT_SUMMARY_MODEL": None,
    "DETECTION_DESCRIPTION_MODEL": None,
    "GENERATION_MODEL": None,
    "DETECTION_MODEL": None,
}

# Necessary lock used for AI actions
MODEL_LOCK = asyncio.Lock()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading models...")
    await asyncio.sleep(1)

    states.MODEL_LOCK = asyncio.Lock()
    states.GENERATION_MODEL = "GenerationModelLoaded"
    states.DETECTION_MODEL = YOLO(full_pretrained_model_path)
    print("Models loaded.")
    yield

    states.GENERATION_MODEL = None
    states.MODEL_LOCK = None
    print("Models shut down.")

app = FastAPI(lifespan=lifespan)

@app.post("/generate", response_model=dict)
async def generate_endpoint(req: ImageGenerationPrompt):
    """Endpoint for generating images from a user prompt."""
    return await generate(req)

@app.post("/detect", response_model=DetectionResponse)
async def detect_endpoint(req: DetectionRequest):
    """Endpoint for detecting weird objects in an image."""
    return await detect(req)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
