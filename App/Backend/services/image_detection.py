# Standard library
import asyncio
import base64
import re
import os
import datetime
import uuid

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
    # Set lock if not already set
    if states.MODEL_LOCK is None:
        states.MODEL_LOCK = asyncio.Lock()

    async with states.MODEL_LOCK:
        # Decode base64 input to NumPy image array
        detect_image = base64_to_image(req.imageBase64)

        # Run YOLO prediction
        print("Running Prediction")
        detection_results = states.DETECTION_MODEL.predict(detect_image)
        result = detection_results[0]
        boxes = result.boxes

        # Check for empty detection
        if boxes is None or len(boxes) == 0:
            print("No objects detected. Saving image.")

            # Convert RGB to BGR
            image_bgr = cv2.cvtColor(detect_image, cv2.COLOR_RGB2BGR)

            # Create a unique filename
            current_directory = os.getcwd()
            path_to_base_directory = re.search(rf"(.*?){"Weird-Stuff-In-Traffic"}", current_directory).group(1)
            filename = f"no_detection_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.jpeg"
            save_path = os.path.join(f"{path_to_base_directory}/App/Backend/failed_images", filename)

            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, image_bgr)

            return DetectionResponse(
                prompt=req.prompt,
                imageBase64=req.imageBase64,
                score=0.0
            )

        # Format the annotated image
        annotated_image = np.array(result.plot())
        img_np = detect_image
        cropped_image = None

        # Crop the first detected object
        for i, box in enumerate(boxes.xyxy):
            x1, y1, x2, y2 = map(int, box[:4])
            cropped_image = img_np[y1:y2, x1:x2]
            break  # Only use the first object for description

        if cropped_image is None:
            cropped_image = detect_image

        # Convert annotated image to base64
        annotated_image_bgr = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
        success, buffer = cv2.imencode('.jpeg', annotated_image_bgr)
        if not success:
            raise ValueError("Failed to encode image.")

        encoded_image = base64.b64encode(buffer).decode('utf-8')

        # Preprocess and generate description
        processed_prompt = preprocess(
            instruction="Please create a list of objects in this image.",
            image_np=cropped_image,
            processor=states.DETECTION_DESCRIPTION_PROCESSOR
        )

        print("Running Summary")
        detection_summary = generate_response(
            processed_prompt,
            states.DETECTION_DESCRIPTION_MODEL,
            states.DETECTION_DESCRIPTION_PROCESSOR,
            device=states.DEVICE
        )

        response = DetectionResponse(
            prompt=req.prompt,
            imageBase64=encoded_image,
            score=float(1 / len(detection_summary)) if detection_summary else 0.0
        )

        return response
