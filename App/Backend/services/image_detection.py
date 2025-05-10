"""services/image_detection.py"""
# Standard library
import asyncio
import base64

# Third-party
import cv2
import numpy as np

# Local application
from schemas.images import DetectionRequest, DetectionResponse
from services import states
from services.image_summary import preprocess, generate_response
from services.image_utils import base64_to_image

### Full Image Detection Pipeline ###

async def detect(req: DetectionRequest) -> DetectionResponse:
    """Function used for detecting weird objects."""
    # Setting Lock if not set
    if states.MODEL_LOCK is None:
        states.MODEL_LOCK = asyncio.Lock()

    # Performing detection
    async with states.MODEL_LOCK:
        # Decode base64 input to NumPy image array
        detect_image = base64_to_image(req.imageBase64)

        # Run YOLO prediction
        print("Running Prediction")
        detection_results = states.DETECTION_MODEL.predict(detect_image)

        # Image formatting
        annotated_image = np.array(detection_results[0].plot())
        boxes = detection_results[0].boxes
        img_np = detect_image
        for i, box in enumerate(boxes.xyxy):
            x1, y1, x2, y2 = map(int, box[:4]) 
            cropped_image = img_np[y1:y2, x1:x2]

        # Convert RGB to BGR before encoding with OpenCV
        annotated_image_bgr = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)

        # Then encode
        success, buffer = cv2.imencode('.jpeg', annotated_image_bgr)
        if not success:
            raise ValueError("Failed to encode image.")

        # Encoded Image
        encoded_image = base64.b64encode(buffer).decode('utf-8')

        # Processing for VLM
        processed_prompt = preprocess(
            instruction="Please create a list of objects in this image.",
            image_np=cropped_image,
            processor=states.DETECTION_DESCRIPTION_PROCESSOR)

        # Summary of detection generated
        print("Running Summary")
        detection_summary = generate_response(processed_prompt, 
                                              states.DETECTION_DESCRIPTION_MODEL, 
                                              states.DETECTION_DESCRIPTION_PROCESSOR, 
                                              device=states.DEVICE)

        # Build response
        response = DetectionResponse(
            prompt=req.prompt,
            imageBase64=encoded_image,
            score=float(1/len(detection_summary))
        )

        return response
