"""services/image_inpainting.py"""

# Imports
import numpy as np
import cv2
import random
from diffusers import DPMSolverMultistepScheduler
import torch
from PIL import Image, ImageDraw, ImageFilter
from services import states

def _parse_polygon_string(polygon_data_string, image_width, image_height):
    '''
    Parses the polygon coordinates from a string, converts them and returns them
    them as a NumPy array.
    '''
    try:
        if not polygon_data_string:
            # print("Error: Empty polygon data string received")
            return None

        parts = polygon_data_string.strip().split()
        if len(parts) < 7:
            # print(f"Error: Invalid format in the string. Too few coordinates.")
            return None

        # Ignore the first number (class ID) and take the rest
        coords_normalized = [float(p) for p in parts[:]]

        if len(coords_normalized) % 2 != 0:
            # print(f"Error: Odd number of coordinates in the string")
            return None

        vertices = []
        for i in range(0, len(coords_normalized), 2):
            nx = coords_normalized[i]
            ny = coords_normalized[i+1]
            # Convert normalized coordinates to pixel coordinates
            x = int(nx * image_width)
            y = int(ny * image_height)
            # Ensure that points remain in the image
            x = max(0, min(image_width - 1, x))
            y = max(0, min(image_height - 1, y))
            vertices.append([x, y])

        return np.array(vertices, dtype=np.int32)

    except ValueError:
        # print(f"Error: The polygon string contains invalid numbers")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while parsing the string: {e}") 
        return None

def _rasterize_polygon(width, height, polygon_vertices):
    """Creates a binary mask of the polygon."""
    mask = np.zeros((height, width), dtype=np.uint8)
    # cv2.fillPoly requires a list of polygons
    cv2.fillPoly(mask, [polygon_vertices], 1) # 1 for pixels within
    return mask

def _calculate_height_map(polygon_mask):
    """Calculates the height of the continuous '1's above each pixel."""
    height, width = polygon_mask.shape
    height_map = np.zeros((height, width), dtype=np.int32)

    for x in range(width):
        # Treat first line directly
        if polygon_mask[0, x] == 1:
            height_map[0, x] = 1

        # Remaining lines
        for y in range(1, height):
            if polygon_mask[y, x] == 1:
                height_map[y, x] = height_map[y - 1, x] + 1
            # else: height_map[y, x] # remains 0 (default value)

    return height_map

def _largest_rectangle_in_histogram(heights):
    """Finds the largest rectangle in a histogram (O(N) algorithm with stack)."""
    stack = [] # Stack stores indices of the bars
    max_area = 0
    # (height, left index in the original histogram, width)
    max_rect_details = (0, 0, 0)

    # Add virtual bars at the beginning/end to handle edge cases
    extended_heights = np.concatenate(([0], heights, [0]))

    for i, h in enumerate(extended_heights):
        while stack and extended_heights[stack[-1]] > h:
            height = extended_heights[stack.pop()]

            width = i - stack[-1] - 1 if stack else i
            if width <= 0: 
                continue

            area = height * width
            if area > max_area:
                max_area = area
               
                original_left_idx = stack[-1] if stack else 0
                max_rect_details = (height, original_left_idx, width)

        if not stack or h > extended_heights[stack[-1]]:
            stack.append(i)
        elif stack and h == extended_heights[stack[-1]]:
            stack[-1] = i

    return max_area, max_rect_details


def _find_largest_inscribed_rectangle(height_map):
    """Iterates through the rows of the height map and finds the largest rectangle."""
    height, width = height_map.shape
    max_area_global = 0
    # Saves (x_min, y_min, x_max, y_max) of the best rectangle
    best_bbox = (0, 0, 0, 0)


    for y in range(height):
        # Histogram for the current line y (represents possible rectangle heights that end at y)
        histogram = height_map[y, :]
        # area: Area of the largest rectangle in the histogram of this line
        # rect_h: Height of this rectangle (corresponds to the value in the histogram)
        # rect_left_idx: Left column (x-coordinate) of the rectangle in the histogram
        # rect_w: Width of this rectangle
        area, (rect_h, rect_left_idx, rect_w) = _largest_rectangle_in_histogram(histogram)

        if area > max_area_global:
            max_area_global = area
            # Conversion of the histogram coordinates into image coordinates
            x_min = rect_left_idx
            x_max = rect_left_idx + rect_w - 1
            y_max = y
            y_min = y - rect_h + 1

            # Validity check (within image boundaries and positive dimension)
            if x_min >= 0 and y_min >= 0 and x_max < width and y_max < height and rect_w > 0 and rect_h > 0:
                best_bbox = (x_min, y_min, x_max, y_max)
            else:
                max_area_global = 0
                best_bbox = (0, 0, 0, 0)

    return max_area_global, best_bbox


def get_suitable_inpaint_area(polygon_data_string, image_width, image_height):
    """
    Calculates the largest inscribed rectangle for a polygon that is passed as a string
    with normalized coordinates.
    """
    # Parse polygon string and convert to pixel coordinates
    poly_verts = _parse_polygon_string(polygon_data_string, image_width, image_height)
    if poly_verts is None or len(poly_verts) < 3:
        print("Fehler: Ungültiges Polygon erhalten.") 
        return None # Ungültiges Polygon

    # Rasterize polygon (creates a mask)
    try:
        poly_mask = _rasterize_polygon(image_width, image_height, poly_verts)
    except Exception as e:
        print(f"Fehler beim Rasterisieren: {e}")
        return None

    # Calculate height map from the mask
    try:
        h_map = _calculate_height_map(poly_mask)
    except Exception as e:
        print(f"Fehler bei der Höhen-Map-Berechnung: {e}") 
        return None

    # Find the largest BBox in the height map
    try:
        max_area, bbox = _find_largest_inscribed_rectangle(h_map)
    except Exception as e:
        print(f"Fehler beim Finden des Rechtecks: {e}") 
        return None

    if max_area > 0:
        x_min, y_min, x_max, y_max = bbox
        if x_max >= x_min and y_max >= y_min and (x_max - x_min) >= 0 and (y_max - y_min) >= 0:
            return bbox
        else:
            print("Warnung: Gefundenes Rechteck hat ungültige Dimensionen.")
            return None # Invalid BBox found
    else:
        print("Kein eingeschriebenes Rechteck gefunden.") 
        return None # no rectangle found


def get_suitable_region(polygons_results, street_image):

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

    return street_image, suitable_inpaint_region_bbox, height_diff

def get_height_diff(polygon, bbox, image_height):
    # compute height difference between suitable inpaint region and polygon
    coords = list(map(float, polygon.strip().split()))
    y_coords = coords[1::2] 
    min_y_normalized = min(y_coords)
    min_y = int(min_y_normalized * image_height)
    return bbox[1] - min_y

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



def create_mask_image(img_w, img_h, x1, y1, x2, y2):
    mask = Image.new("L", (img_w, img_h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle([x1, y1, x2, y2], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(50))
    return mask


def realvisxl_inpaint(image, bbox, user_prompt, strength, g_scale):

    x1, y1, x2, y2 = bbox

    styling_prompt = (
        ", central position, size proportional to the surrounding, ultra-realistic photo, integration with natural shadows, "
        "realistic reflections, consistent ambient lighting, matching camera angle and focal depth. "
        "Preserve street texture and geometric alignment. crisp detail, "
        "subtle gradients, consistent color tones, background integrety."
    )
    negative_prompt = (
        "big, huge, oversized objects, blurry, low resolution, poor detail, artifacts, double edges, distorted anatomy, extra limbs, "
        "unrealistic lighting, harsh shadows, incorrect perspective, CGI, animation, "
        "exaggerated pose, fake texture, logo, watermark, text, grainy, tiling, "
        "disconnected background, disjointed integration, bad shadow, plastic look, out of place, half generated, missing limbs"
    )

    mask_image = create_mask_image(image.size[0], image.size[1], x1, y1, x2, y2)

    # visualize mask for inpainting
    # draw = ImageDraw.Draw(mask_image)
    # draw.rectangle((x1, y1, x2, y2), outline='green', width=5)
    # mask_image.save("G:/weirdstuffintraffic/mask_image.png")

    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()

    #pylint: disable=not-callable
    result = states.GENERATION_MODEL(
        prompt=user_prompt + styling_prompt,
        negative_prompt=negative_prompt,
        image=image,
        mask_image=mask_image,
        strength=strength,
        num_inference_steps=40,
        guidance_scale=g_scale,
        height=896,
        width=1600,
        inpaint_full_res=True,
        inpaint_full_res_padding=32,
        # generator=torch.Generator("cuda").manual_seed(42)
    )

    return result.images[0]
