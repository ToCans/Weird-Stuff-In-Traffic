import cv2
import base64

def generate_canny_map(image_path, low_thresh=100, high_thresh=200):
    """
    Generates a Canny edge map from the given image and returns it as base64-encoded PNG.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image at path: {image_path}")

    blurred = cv2.GaussianBlur(img, (5, 5), 1.0)
    edges = cv2.Canny(blurred, low_thresh, high_thresh)

    _, buffer = cv2.imencode(".png", edges)
    return base64.b64encode(buffer).decode("utf-8")