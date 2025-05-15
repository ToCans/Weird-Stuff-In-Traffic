import numpy as np
import cv2
import math


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
        # print(f"An unexpected error occurred while parsing the string: {e}") 
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
            if width <= 0: continue

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
    

