from realvisxl import realvisxl_inpaint
from get_biggest_bbox_inside_polygon import get_suitable_inpaint_area
from PIL import Image, ImageDraw
import time
from ultralytics import YOLO
import random
import json
import base64
from io import BytesIO
import os

street_image_folder_path = "change/to/street_image/directory"
yolo_model_path = "change/to/model/location"

# load yolo model
street_detection_yolo_model = YOLO(yolo_model_path)


def get_image_and_suitable_region(all_street_image_paths, image_cache):

    image_path = random.choice(all_street_image_paths)

    # check if already in cache
    if image_path in image_cache:
        return image_cache[image_path]
    
    # otherwise load image
    street_image = Image.open(image_path).convert("RGB")

    # and get street polygon
    polygons_results = street_detection_yolo_model.predict(
        source=street_image, 
        task='segment', 
        verbose=False, 
        conf=0.25
    )

    # extract polygon out of yolo output
    for result in polygons_results:
        for polygon in result.masks.xy:
            scaled_polygon = []
            for point in polygon:
                normalized_point = (point[0] / street_image.width, point[1] / street_image.height)
                scaled_polygon.append(f"{normalized_point[0]} {normalized_point[1]}")
            
            final_polygon = " ".join(scaled_polygon)

    # and get biggest bounding box inside polygon
    suitable_inpaint_region_bbox = get_suitable_inpaint_area(final_polygon, street_image.width, street_image.height)

    # and compute height difference for better inpaint bbox placement
    height_diff=get_height_diff(final_polygon, suitable_inpaint_region_bbox, street_image.height)

    # and cache new loaded data
    image_cache[image_path] = (street_image, final_polygon, suitable_inpaint_region_bbox, height_diff)

    return street_image, final_polygon, suitable_inpaint_region_bbox, height_diff


def get_random_bbox_within_bbox(bbox, min_width, max_width, min_height, max_height, height_diff, image_size):

    x1, y1, x2, y2 = bbox

    # random center point inside bbox
    xc = random.uniform(x1+0.2*(x2-x1), x2-0.2*(x2-x1))
    yc = random.uniform(y1, y2)

    # random with and height
    width = random.uniform(min_width, max_width)
    height = random.uniform(min_height, max_height)

    # clip bbox size to image size to prevent a bigger bbox than image
    new_x1 = int(max(xc - width / 2, 0))
    new_y1 = int(max(yc - height / 2 - height_diff*1.5, 0))
    new_x2 = int(min(xc + width / 2, image_size[0]))
    new_y2 = int(min(yc + height / 2 + height_diff*1.5, image_size[1]))

    return (new_x1, new_y1, new_x2, new_y2)


def visualize(polygon, suitable_inpaint_region_bbox, inpaint_bbox, image, save_path, height_diff):

    draw = ImageDraw.Draw(image)

    # draw suitable inpaint region bbox
    draw.rectangle(suitable_inpaint_region_bbox, outline='green', width=5)

    # draw inpaint bbox
    draw.rectangle(inpaint_bbox, outline='red', width=5)

    # draw inpaint bbox center
    xc = int((inpaint_bbox[2]-inpaint_bbox[0])/2 + inpaint_bbox[0])
    yc = int((inpaint_bbox[3]-inpaint_bbox[1])/2 + inpaint_bbox[1])
    draw.rectangle((xc, yc, xc, yc), outline='blue', width=2)
    # draw original selected point
    yc += height_diff*1.5
    draw.rectangle((xc, yc, xc, yc), outline=(10, 100, 180), width=2)

    # draw polygon
    polygon_coords = list(map(float, polygon.split()))
    polygon_points = [
        (polygon_coords[i] * image.width, polygon_coords[i+1] * image.height)
        for i in range(0, len(polygon_coords), 2)
    ]
    draw.polygon(polygon_points, outline="yellow", width=3)

    # save image with bboxes
    image.save(save_path)
    print(f"Visualized image saved to {save_path}")


def inpaint_image(street_image, bbox, user_prompt):

    x1, y1, x2, y2 = bbox

    inpainted_image = realvisxl_inpaint(x1, y1, x2, y2, street_image, user_prompt)

    return inpainted_image

def get_height_diff(polygon, bbox, image_height):
    # compute height difference between suitable inpaint region and polygon
    coords = list(map(float, polygon.strip().split()))
    y_coords = coords[1::2] 
    min_y_normalized = min(y_coords)
    min_y = int(min_y_normalized * image_height)
    return bbox[1] - min_y



# main pipeline
def inpaint_pipeline(prompt_list, num_images_per_prompt, same_image_per_promt=False):

    # load all images from folder
    all_street_image_paths = [
        os.path.join(street_image_folder_path, f)
        for f in os.listdir(street_image_folder_path)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    # cache for images to prevent double loading
    image_cache = {}

    results = []

    # iterate over prompts and do inpainting for every prompt
    for prompt in prompt_list:

        # loads one image per prompt
        if same_image_per_promt:
            # get image, polygon and suitable bbox
            street_image, polygon, suitable_inpaint_region_bbox, height_diff = get_image_and_suitable_region(all_street_image_paths, image_cache)

        for i in range(num_images_per_prompt):
            
            # loads one image per inpaint operation
            if not same_image_per_promt:
                # get image, polygon and suitable bbox
                street_image, polygon, suitable_inpaint_region_bbox, height_diff = get_image_and_suitable_region(all_street_image_paths, image_cache)

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

            # inpaint image
            inpainted_image = inpaint_image(street_image.copy(), inpaint_bbox, prompt)

            # visualize all bboxes on inpainted image
            # visualize(
            #     polygon=polygon, 
            #     suitable_inpaint_region_bbox=suitable_inpaint_region_bbox, 
            #     inpaint_bbox=inpaint_bbox, 
            #     image=inpainted_image.copy(), 
            #     save_path=f"G:/weirdstuffintraffic/results/street_image_with_bboxes_{prompt_list.index(prompt)}_{i}.png", 
            #     height_diff=height_diff
            # )

            # encode inpainted image in base64
            buffered = BytesIO()
            inpainted_image.save(buffered, format="PNG")
            inpainted_image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # save results
            results.append({
                "prompt": prompt,
                "inpaint_bbox_xyxy": list(inpaint_bbox),
                "inpainted_image": inpainted_image_base64
            })

    return results


if __name__ == "__main__":

    example_prompts = [
        "A pink elephant in a suit reading a newspaper in the middle of the road.",
        "A toast car driven by a bee.",
        "A group of penguins waiting at a bus stop.",
        "A giant goldfish floating in a water bubble above the street.",
        "A dinosaur wearing a safety vest directing traffic."
    ]

    results = inpaint_pipeline(example_prompts, 4, same_image_per_promt=False)

    # save json
    output_path = "change/to/saving/directory/for/output.json"
    with open(output_path, "w") as f:
        json.dump(results, f)

    print(f"Saved {len(results)} results to {output_path}")