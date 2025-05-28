import json
import cv2
import os
import random
import argparse
from matplotlib import pyplot as plt

def visualize_coco_annotations(image_path, json_path, output_dir=None):
    """
    Visualize COCO annotations on images
    
    Args:
        image_path (str): Path to the image file or directory containing images
        json_path (str): Path to the COCO JSON annotations file
        output_dir (str, optional): Directory to save visualized images
    """
    # Load COCO annotations
    with open(json_path) as f:
        coco_data = json.load(f)
    
    # Create mappings
    img_name_to_id = {img['file_name']: img['id'] for img in coco_data['images']}
    cat_id_to_name = {cat['id']: cat['name'] for cat in coco_data['categories']}
    colors = {cat_id: (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
              for cat_id in cat_id_to_name.keys()}
    
    # Determine if input is directory or single image
    if os.path.isdir(image_path):
        image_files = [f for f in os.listdir(image_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    else:
        image_files = [os.path.basename(image_path)]
        image_path = os.path.dirname(image_path)
    
    # Process each image
    for img_file in image_files:
        # Load image
        img_full_path = os.path.join(image_path, img_file)
        image = cv2.imread(img_full_path)
        
        if image is None:
            print(f"Could not read image: {img_full_path}")
            continue
            
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get image ID from annotations
        if img_file not in img_name_to_id:
            print(f"Image {img_file} not found in annotations")
            continue
            
        img_id = img_name_to_id[img_file]
        annotations = [ann for ann in coco_data['annotations'] if ann['image_id'] == img_id]
        
        # Draw annotations
        for ann in annotations:
            bbox = ann['bbox']
            x, y, w, h = map(int, bbox)
            cat_id = ann['category_id']
            cat_name = cat_id_to_name[cat_id]
            color = colors[cat_id]
            
            # Draw bounding box and label
            cv2.rectangle(image, (x, y), (x+w, y+h), color, 2)
            label = f"{cat_name}"
            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(image, (x, y - text_height - 5), (x + text_width, y), color, -1)
            cv2.putText(image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Display or save result
        plt.figure(figsize=(12, 8))
        plt.imshow(image)
        plt.axis('off')
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"annotated_{img_file}")
            plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
            plt.close()
            print(f"Saved annotated image to: {output_path}")
        else:
            plt.show()
            plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize COCO annotations on images')
    parser.add_argument('--image', type=str, required=True, 
                       help='Path to the image file or directory containing images')
    parser.add_argument('--json', type=str, required=True, 
                       help='Path to COCO JSON annotations file')
    parser.add_argument('--output', type=str, default=None, 
                       help='Directory to save visualized images')
    
    args = parser.parse_args()
    visualize_coco_annotations(args.image, args.json, args.output)