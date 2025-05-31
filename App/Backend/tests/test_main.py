"""tests/main_test.py"""

# Imports
import base64
import io
import sys
import os
from unittest.mock import patch
from PIL import Image
from fastapi.testclient import TestClient

# Add the parent directory (App/Backend) to sys.path to make `main` importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#pylint: disable=wrong-import-position
from main import app

def encode_image_to_base64(image_path: str) -> str:
    """Utility Function for encoding image to string"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

# Test Client Detection
def test_detect_endpoint():
    """Testing Detect Endpoint"""
    with patch("services.image_detection.detect") as mock_detect:
        mock_detect.return_value = {"result": "detection_success"}

        # Using a test image and preparing JSON
        selected_image_path = "/home/tom/Desktop/Programming/Shared/Weird-Stuff-In-Traffic/Data/yolo/coco8/images/train/000000000025.jpg"
        base64_image = encode_image_to_base64(selected_image_path)
        json_to_send = {"prompt":"Please create an image of a giraffe", "imageBase64": base64_image}

        # POST Request
        response = client.post("/detect", json=json_to_send)
        response_data = response.json()

        # Decode base64 back to image
        img_data = base64.b64decode(response_data["imageBase64"])
        image = Image.open(io.BytesIO(img_data))

        # Output Check
        print(f"Response:\n{response_data}")
        image.save("test_output.jpg")

# Test Client Detection
def test_generate_endpoint():
    """Testing Generate Endpoint"""
    with patch("services.image_generation.generate") as mock_detect:
        mock_detect.return_value = {"result": "generation_success"}

        # Using one of Hamza's prompts
        user_prompt = "A panda juggles on the middle lane."
        json_to_send = {"prompt": user_prompt}

        # POST Request
        response = client.post("/generate", json=json_to_send)
        response_data = response.json()

        # Output Check
        print(f"Response:\n{response_data}")

with TestClient(app) as client:
    test_generate_endpoint()
