import os
import cv2
import glob
import numpy as np
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description='Visualize YOLO annotations')
    parser.add_argument('--image_dir', type=str, required=True, help='Directory containing images')
    parser.add_argument('--label_dir', type=str, required=True, help='Directory containing YOLO label files')
    parser.add_argument('--output_dir', type=str, default='output_visualizations', help='Output directory for visualizations')
    parser.add_argument('--class_names', type=str, default=None, help='File containing class names (one per line)')
    parser.add_argument('--segmentation', action='store_true', help='Visualize segmentation masks instead of bounding boxes')
    return parser.parse_args()

def load_class_names(class_file):
    if class_file and os.path.exists(class_file):
        with open(class_file, 'r') as f:
            return [line.strip() for line in f.readlines()]
    return None

def draw_yolo_bbox(image, annotation, class_names=None):
    height, width = image.shape[:2]
    class_id, x_center, y_center, w, h = map(float, annotation.split())
    
    # Convert YOLO coordinates to pixel coordinates
    x_center *= width
    y_center *= height
    w *= width
    h *= height
    
    x_min = int(x_center - w/2)
    y_min = int(y_center - h/2)
    x_max = int(x_center + w/2)
    y_max = int(y_center + h/2)
    
    # Generate random color based on class ID for consistency
    np.random.seed(int(class_id))
    color = tuple(map(int, np.random.randint(0, 255, 3)))
    
    # Draw rectangle
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color, 2)
    
    # Create label
    label = f"{class_names[int(class_id)]}" if class_names else f"Class {int(class_id)}"
    
    # Display label
    (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    cv2.rectangle(image, (x_min, y_min - text_height - 10), (x_min + text_width, y_min), color, -1)
    cv2.putText(image, label, (x_min, y_min - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def draw_yolo_segmentation(image, annotation, class_names=None):
    height, width = image.shape[:2]
    parts = list(map(float, annotation.split()))
    class_id = int(parts[0])
    points = parts[1:]
    
    # Reshape points and scale to image dimensions
    points = np.array(points).reshape(-1, 2)
    points[:, 0] *= width
    points[:, 1] *= height
    points = points.astype(np.int32)
    
    # Generate random color based on class ID
    np.random.seed(class_id)
    color = tuple(map(int, np.random.randint(0, 255, 3)))
    
    # Draw polygon
    cv2.polylines(image, [points], isClosed=True, color=color, thickness=2)
    
    # Fill polygon with transparency
    overlay = image.copy()
    cv2.fillPoly(overlay, [points], color)
    alpha = 0.3  # Transparency factor
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
    
    # Create label
    label = f"{class_names[class_id]}" if class_names else f"Class {class_id}"
    
    # Display label at first point
    (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    label_x = points[0][0]
    label_y = points[0][1] - 10 if points[0][1] - 10 > text_height else points[0][1] + 20
    
    cv2.rectangle(image, (label_x, label_y - text_height - 10), 
                 (label_x + text_width, label_y), color, -1)
    cv2.putText(image, label, (label_x, label_y - 5), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def visualize_yolo_annotations(args):
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load class names if provided
    class_names = load_class_names(args.class_names)
    
    # Get all image files
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(glob.glob(os.path.join(args.image_dir, ext)))
    
    for image_path in image_paths:
        # Get corresponding label file
        label_path = os.path.join(args.label_dir, f"{Path(image_path).stem}.txt")
        
        if not os.path.exists(label_path):
            print(f"No label file found for {image_path}")
            continue
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to read image: {image_path}")
            continue
        
        # Read annotations
        with open(label_path, 'r') as f:
            annotations = f.readlines()
        
        # Draw each annotation
        for ann in annotations:
            if args.segmentation:
                draw_yolo_segmentation(image, ann, class_names)
            else:
                draw_yolo_bbox(image, ann, class_names)
        
        # Save visualized image
        output_path = os.path.join(args.output_dir, f"vis_{Path(image_path).name}")
        cv2.imwrite(output_path, image)
        print(f"Saved visualization to {output_path}")

if __name__ == '__main__':
    args = parse_args()
    visualize_yolo_annotations(args)