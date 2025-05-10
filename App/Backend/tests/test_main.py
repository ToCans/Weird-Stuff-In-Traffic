"""tests/main_test.py"""
import base64
import io
from unittest.mock import patch
from PIL import Image
from main import app
from fastapi.testclient import TestClient

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
        json_to_send = {"prompt":"Please create an image of a giraffe.", "imageBase64": base64_image}

        # POST Request
        response = client.post("/detect", json=json_to_send)
        response_data = response.json()

        # Decode base64 back to image
        img_data = base64.b64decode(response_data["imageBase64"])
        image = Image.open(io.BytesIO(img_data))

        # Output Check
        print(f"Response:\n{response_data}")
        image.save("test_output.jpg")

with TestClient(app) as client:
    test_detect_endpoint()
