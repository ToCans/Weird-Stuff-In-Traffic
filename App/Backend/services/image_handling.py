"""services/image_handling.py"""
import asyncio
import base64
import io
from PIL import Image
import cv2
import numpy as np
from services import states
from schemas.images import ImageGenerationPrompt, DetectionRequest, DetectionResponse

def encode_image_array_to_base64(image_array: np.ndarray, image_format: str = "jpeg") -> str:
    """
    Encodes a uint8 image array to a base64 string.
    
    Args:
        image_array (np.ndarray): The image as a uint8 NumPy array (H x W x C).
        image_format (str): Image format to encode (e.g., 'jpeg', 'png').
    
    Returns:
        str: Base64-encoded string of the image.
    """
    success, buffer = cv2.imencode(f".{image_format}", image_array)
    if not success:
        raise ValueError("Could not encode image array.")

    encoded_string = base64.b64encode(buffer).decode("utf-8")
    return encoded_string

def base64_to_image(base64_str):
    """Decode base64 string to a NumPy array image."""
    image_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(image_data))
    return np.array(image)

async def detect(req: DetectionRequest) -> DetectionResponse:
    """Function used for detecting weird objects"""
    
    if states.MODEL_LOCK is None:
        states.MODEL_LOCK = asyncio.Lock()
    
    async with states.MODEL_LOCK:
        # Decode base64 input to NumPy image array
        detect_image = base64_to_image(req.imageBase64)  # shape (H, W, C), dtype uint8
        
        # Run YOLO prediction
        results = states.DETECTION_MODEL.predict(detect_image)
        
        # Draw bounding boxes on image
        result_image = np.array(results[0].plot())  # Ensure it's a NumPy array
        
        # Encode the result image to base64
        success, buffer = cv2.imencode('.jpeg', result_image)
        if not success:
            raise ValueError("Failed to encode image.")
        
        encoded_string = base64.b64encode(buffer).decode('utf-8')
        
        # Build response
        response = DetectionResponse(
            prompt=req.prompt,
            imageBase64=encoded_string,
            score=0.69
        )
        
        return response
  

async def generate(req: ImageGenerationPrompt):
    '''Function used for generating images from user prompt'''

    # Optionally lock if accessing/updating shared state
    if states.MODEL_LOCK is None:
        states.MODEL_LOCK = asyncio.Lock()

    # Optionally lock if accessing/updating shared state
    async with states.MODEL_LOCK:
        # Simulate inference
        result = f"Prediction for '{req.text}' using {states.GENERATION_MODEL}"

    return {"result": result}
