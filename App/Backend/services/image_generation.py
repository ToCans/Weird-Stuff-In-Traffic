"""services/image_generation.py"""

# Standard library
import asyncio
from io import BytesIO
import base64
import json

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
        
        # Saving process inside of a JSON
        output_json_filename = "output_gen.json"
        try:
            with open(output_json_filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4)
            print(f"\n All results successfully saved in '{output_json_filename}'.")
        except Exception as e:
            print(f"Error when saving the JSON: {e}")


        return states.USER_PROMPT_SUMMARY
