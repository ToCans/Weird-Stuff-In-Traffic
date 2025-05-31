"""services/image_generation.py"""

# Standard library
import asyncio
from io import BytesIO
import base64
import os

# Third-party
from PIL import Image

# Local application
from schemas.images import ImageGenerationPrompt, GeneratedImage, GeneratedImages
from services import states
from services.prompt_summary import extract_nouns_with_counts
from services.image_inpainting import get_suitable_region, get_random_bbox_within_bbox, inpaint_image

async def generate(req: ImageGenerationPrompt) -> GeneratedImages:
    """Function used for generating weird images."""
    # Set lock if not already set
    if states.BACKEND_LOCK is None:
        states.BACKEND_LOCK = asyncio.Lock()

    async with states.BACKEND_LOCK:
        # Extracting the main nouns from the user's prompt
        states.USER_PROMPT_SUMMARY = extract_nouns_with_counts(req.prompt)

        """

        # Suitable Reason Detection
        street_image = Image.open("/home/tom/Desktop/Programming/Shared/Weird-Stuff-In-Traffic/Data/images/street-images/0a0a0b1a-7c39d841.jpg").convert("RGB")

        print("Predicting Street Polygons")
        polygons_results = states.STREET_DETECTION_MODEL.predict(
            source=street_image,
            task='segment',
            verbose=False,
            conf=0.25
        )

        
        street_image, suitable_inpaint_region_bbox, height_diff = get_suitable_region(polygons_results, street_image)

        results = []
        strength = 0.6

        for i in range(4):
            # get random fitting bbox for inpainting
            inpaint_bbox = get_random_bbox_within_bbox(
                        bbox=suitable_inpaint_region_bbox, 
                        min_width=street_image.width*0.4, 
                        max_width=street_image.width*0.7, 
                        min_height=street_image.height*0.4, 
                        max_height=street_image.height*0.7,
                        height_diff=height_diff,
                        image_size=street_image.size
                )

            # Inpainting the image
            print("Attempting Inpainting")
            inpainted_image = inpaint_image(street_image.copy(), inpaint_bbox, req.prompt, strength)
            strength = max(1, strength + 0.1)
            buffered = BytesIO()
            inpainted_image.save(buffered, format="PNG")
            inpainted_image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            results.append({
                "image_number": i + 1, 
                "prompt": req.prompt,
                "prompt subjects": states.USER_PROMPT_SUMMARY, 
                "inpaint_bbox_xyxy": list(inpaint_bbox),
                "inpainted_image": inpainted_image_base64
            })
            print(f"Picture {i + 1} successfully processed")

        
        
        print(f"\nAll {len(results)} pictures successfully processed ")
        """

        # Pretending to generate images
        directory = "/home/tom/Desktop/Programming/Shared/Weird-Stuff-In-Traffic/Data/yolo/coco8/images/train"
        generated_images = []
        for filename in os.listdir(directory):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_path = os.path.join(directory, filename)
                with Image.open(image_path) as img:
                    buffered = BytesIO()
                    img.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    generated_images.append(GeneratedImage(prompt=req.prompt, imageBase64=img_base64))
        return GeneratedImages(images=generated_images)

