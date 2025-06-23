"""services/image_utils.py"""
import base64
import io
from PIL import Image
import numpy as np

def base64_to_image(base64_str, size=(1600, 800)):
    """Decode base64 string to resized NumPy array image (RGB)."""
    # Strip data URL scheme if present
    if base64_str.startswith("data:image"):
        base64_str = base64_str.split(",", 1)[1]

    image_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(image_data)).convert("RGB")

    if size:
        image = image.resize(size, Image.BILINEAR)

    return np.array(image) 

