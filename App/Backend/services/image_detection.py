"""services/image_detection.py"""

# Standard library
import asyncio
import base64
import re
import os
import datetime
import uuid
import ast

# Third-party
import cv2
from detectron2.utils.visualizer import Visualizer, ColorMode
from detectron2.data import MetadataCatalog

# Local application
from schemas.images import DetectionRequest, DetectionResponse
from models.configurations import test_metadata
from services import states
from services.image_summary import preprocess, generate_response
from services.image_utils import base64_to_image

### Full Image Detection Pipeline ###

async def detect(req: DetectionRequest) -> DetectionResponse:
    """Function used for detecting weird objects."""
    # Set lock if not already set
    if states.BACKEND_LOCK is None:
        states.BACKEND_LOCK = asyncio.Lock()

    async with states.BACKEND_LOCK:
        # Decode base64 input to NumPy image array
        detect_image = base64_to_image(req.imageBase64)

        # Run Detectron2 Prediction
        print("Running Prediction")
        outputs = states.WEIRD_DETECTION_MODEL(detect_image)

        print("Prediction Outputs:", outputs)

        instances = outputs["instances"].to("cpu")
        boxes = instances.pred_boxes if instances.has("pred_boxes") else None

        if boxes is None or len(boxes) == 0:
            print("No objects detected. Saving image.")
            image_bgr = cv2.cvtColor(detect_image, cv2.COLOR_RGB2BGR)

            current_directory = os.getcwd()
            match = re.search(rf"(.*?){'Weird-Stuff-In-Traffic'}", current_directory)
            path_to_base_directory = match.group(1) if match else current_directory

            filename = f"no_detection_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.jpeg"
            save_path = os.path.join(path_to_base_directory, "Weird-Stuff-In-Traffic/App/Backend/failed_images", filename)

            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, image_bgr)

            return DetectionResponse(
                prompt=req.prompt,
                imageBase64=req.imageBase64,
                score=1.0
            )

        # Annotate image
        v = Visualizer(
            detect_image[:, :, ::-1],  # Convert RGB to BGR for Detectron2
            metadata=test_metadata,   # should contain .thing_classes
            scale=1.0,
            instance_mode=ColorMode.IMAGE
        )
        out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
        annotated_image = out.get_image()[:, :, ::-1]  # Convert back to RGB

        # Extract boxes
        boxes = outputs["instances"].pred_boxes if outputs["instances"].has("pred_boxes") else []

        # Crop the first detected object
        cropped_image = detect_image
        if len(boxes) > 0:
            x1, y1, x2, y2 = map(int, boxes.tensor[0])
            cropped_image = detect_image[y1:y2, x1:x2]

        # Encode annotated image to base64 JPEG
        annotated_image_bgr = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
        success, buffer = cv2.imencode('.jpeg', annotated_image_bgr)
        if not success:
            raise ValueError("Failed to encode image.")

        encoded_image = base64.b64encode(buffer).decode('utf-8')
        image_base64_with_header = f"data:image/jpeg;base64,{encoded_image}"

        # Prompt preprocessing and generation (unchanged)
        processed_prompt = preprocess(
            instruction="Please create a list of objects in this image.",
            image_np=cropped_image,
            processor=states.DETECTION_DESCRIPTION_PROCESSOR
        )

        detection_summary = generate_response(
            processed_prompt,
            states.DETECTION_DESCRIPTION_MODEL,
            states.DETECTION_DESCRIPTION_PROCESSOR,
            device=states.DEVICE
        )

        eval_detection_summary = ast.literal_eval(detection_summary)

        # Normalize to lowercase
        user_requested_set = set(item.lower() for item in  states.USER_PROMPT_SUMMARY)
        predicted_set = set(item.lower() for item in eval_detection_summary)



        # Compare
        matches = user_requested_set & predicted_set
        recall = len(matches) / len(user_requested_set) if user_requested_set else 0.0

        # Scoring
        if isinstance(eval_detection_summary, list):
            if recall != 0.0:
            # 0.5 for getting a detection right
                score = 50.0 + round(50 * recall, 2)
            else:
                score = 50.0
        else:
            score = 100.0

        print("User Requested Set:", user_requested_set)
        print("Predicted Set:", predicted_set)
        print("Score:", score)
        print("Recall:", recall)

        return DetectionResponse(
            prompt=req.prompt,
            imageBase64=image_base64_with_header,
            score=score
        )
