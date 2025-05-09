"""main_test.py"""
import base64
from unittest.mock import patch
from main import app
from fastapi.testclient import TestClient

def encode_image_to_base64(image_path: str) -> str:
    """Utility Function for encoding image to string"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

# Test Client Init
def test_detect_endpoint():
    """Testing Detect Endpoint"""
    with patch("services.image_handling.detect") as mock_detect:
        mock_detect.return_value = {"result": "detection_success"}
        selected_image_path = "/home/tom/Desktop/Programming/Shared/Weird-Stuff-In-Traffic/Data/yolo/coco8/images/train/000000000025.jpg"
        base64_image = encode_image_to_base64(selected_image_path)
        json_to_send = {"prompt":"please create an image of a gnome.", "imageBase64": base64_image}

        response = client.post("/detect", json=json_to_send)
        print(response)

with TestClient(app) as client:
    test_detect_endpoint()
