"""services/image_generation.py"""

# Standard library
import asyncio
from io import BytesIO
import base64
import os
import random

# Third-party
from PIL import Image

# Local application
from schemas.images import ImageGenerationPrompt, GeneratedImage, GeneratedImages
from services import states
from services.prompt_summary import extract_nouns_with_counts
from services.image_inpainting import get_suitable_region, get_random_bbox_within_bbox, realvisxl_inpaint

async def generate(req: ImageGenerationPrompt) -> GeneratedImages:
    """Function used for generating weird images."""
    # Set lock if not already set
    if states.BACKEND_LOCK is None:
        states.BACKEND_LOCK = asyncio.Lock()

    async with states.BACKEND_LOCK:
        # Extracting the main nouns from the user's prompt
        states.USER_PROMPT_SUMMARY = extract_nouns_with_counts(req.prompt)

        # Randomly select street image from dataset
        street_image_folder_path = "/home/ai-team2/Weird-Stuff-In-Traffic/App/Backend/images/background_images"
        all_street_image_paths = [
            os.path.join(street_image_folder_path, f)
            for f in os.listdir(street_image_folder_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
        image_path = random.choice(all_street_image_paths)
        street_image = Image.open(image_path).convert("RGB")

        # Gathering Suitable Region for Inpainting
        polygons_results = states.STREET_DETECTION_MODEL.predict(
            source=street_image,
            task='segment',
            verbose=False,
            conf=0.25
        )
        street_image, suitable_inpaint_region_bbox, height_diff = get_suitable_region(polygons_results, street_image)

        # Generation of images

        generated_images = []

        strengths = [0.5,  0.55,  0.55,  0.6]
        g_scales =  [11.0,  11,  6,  4]


        for i in range(4):
            # get random fitting bbox for inpainting
            inpaint_bbox = get_random_bbox_within_bbox(
                        bbox=suitable_inpaint_region_bbox,
                        min_width=street_image.width*0.5,
                        max_width=street_image.width*0.9,
                        min_height=street_image.height*0.5,
                        max_height=street_image.height*0.9,
                        height_diff=height_diff,
                        image_size=street_image.size
                )

            # Inpainting the image
            print("Attempting Inpainting")
            inpainted_image = realvisxl_inpaint(street_image.copy(), inpaint_bbox, req.prompt, strengths[i], g_scales[i])
            buffered = BytesIO()
            inpainted_image.save(buffered, format="PNG")

            # Encoding and Creating GeneratedImage object
            inpainted_image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            generated_images.append(GeneratedImage(prompt=req.prompt,imageBase64=inpainted_image_base64))


        print(f"\nAll {len(generated_images)} pictures successfully processed ")

        return GeneratedImages(images=generated_images)
