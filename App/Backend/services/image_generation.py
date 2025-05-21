"""services/image_generation.py"""

# Standard library
import asyncio
from io import BytesIO

# Third-party
from PIL import Image

# Local application
from schemas.images import ImageGenerationPrompt, GeneratedImages
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

        # Suitable Reason Detection
        street_image = Image.open("/home/tom/Desktop/Programming/Shared/Weird-Stuff-In-Traffic/Data/images/street-images/0a0a0b1a-7c39d841.jpg").convert("RGB")

        print("Predicting Street Polygons")
        polygons_results = states.STREET_DETECTION_MODEL.predict(
            source=street_image,
            task='segment',
            verbose=False,
            conf=0.25
        )

        print(polygons_results)

        street_image, suitable_inpaint_region_bbox, height_diff = get_suitable_region(polygons_results, street_image)

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
        inpainted_image = inpaint_image(street_image.copy(), inpaint_bbox, req.prompt)
        buffered = BytesIO()
        inpainted_image.save(buffered, format="PNG")

        return states.USER_PROMPT_SUMMARY
