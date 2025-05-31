"""services/image_utils.py"""
import base64
import io
from PIL import Image
import numpy as np

def base64_to_image(base64_str):
    """Decode base64 string to a NumPy array image."""
    image_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(image_data))
    return np.array(image)
