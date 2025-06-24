import os
import shutil
import json
import cv2
from pathlib import Path
import argparse
from ultralytics import YOLO
from tqdm import tqdm


class Annotator:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect(self, img_paths, images_in_memory=True, include_no_detections=True):
        return [self.model(img_path) for img_path in img_paths]

    def save_labelme_annotation(self, img_path, output_dir, conf, move_images=False):
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        img = cv2.imread(img_path)
        
        # Perform detection
        results = self.model(img, conf=conf, verbose=False)
        img_filename = os.path.basename(img_path)
        img_width, img_height = img.shape[1], img.shape[0]
        json_annotations = []

        if results and len(results[0].boxes) > 0:
            for box, cls in zip(results[0].boxes.xyxy.cpu().numpy(), results[0].boxes.cls.cpu().numpy()):
                bbox_points = [
                    [int(box[0]), int(box[1])],
                    [int(box[2]), int(box[3])]
                ]
                annotation = {
                    "label": self.model.names[int(cls)],  # Use the predicted class name
                    "points": bbox_points,
                    "group_id": None,
                    "shape_type": "rectangle",
                    "flags": {}
                }
                json_annotations.append(annotation)

        annotation_data = {
            "version": "0.3.3",
            "flags": {},
            "shapes": json_annotations,
            "imagePath": img_filename,
            "imageData": None,
            "imageHeight": img_height,
            "imageWidth": img_width,
        }

        # Save to JSON file
        json_filename = os.path.join(output_dir, f"{Path(img_path).stem}.json")
        with open(json_filename, 'w') as f:
            json.dump(annotation_data, f, indent=4)

        # Optionally copy the image to the output directory
        if move_images:
            output_image_path = os.path.join(output_dir, img_filename)
            shutil.copy(img_path, output_image_path)

    def save_yolo_annotations(self, img_dir, output_dir, conf, move_images=False):
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # List all image files in the source directory
        images = [f for f in os.listdir(img_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]

        if not images:
            return  # No valid images to process

        for img_file in images:
            img_path = os.path.join(img_dir, img_file)
            img = cv2.imread(img_path)
            if img is None:
                print(f"Failed to read image {img_path}")
                continue

            # Perform detection
            results = self.model(img, conf=conf, verbose=False)

            # Determine the output .txt filename
            txt_filename = os.path.join(output_dir, f"{Path(img_path).stem}.txt")

            # Write annotations to the YOLO format
            with open(txt_filename, 'w') as file:
                if len(results) > 0 and len(results[0].boxes) > 0:
                    for bbox, cls in zip(results[0].boxes.xywhn.cpu().numpy(), results[0].boxes.cls.cpu().numpy()):
                        x_center, y_center, width, height = bbox[:4]
                        class_index = int(cls)  # Use the predicted class index
                        file.write(f"{class_index} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

            # Copy the image to the output directory if --move_images is specified
            if move_images:
                destination_image_path = os.path.join(output_dir, img_file)
                shutil.copy(img_path, destination_image_path)  # Copy the image to the output directory





def main():
    parser = argparse.ArgumentParser(description="Annotate images using YOLO and save annotations to JSON files.")
    parser.add_argument("--src_dir", type=str, required=True, help="Source directory containing images.")
    parser.add_argument("--dst_dir", type=str, required=True, help="Destination directory to save annotations.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the YOLO model.")
    parser.add_argument("--conf", type=float, default=0.9, help="Confidence threshold for predictions.")    
    parser.add_argument("--move_images", action='store_true', help="Move images to the destination directory.")
    parser.add_argument("--annotation_mode", type=str, required=True, help="Annotation mode: 'labelme', 'yolo', or 'all'.")

    args = parser.parse_args()

    annotator = Annotator(args.model_path)

    if os.path.isdir(args.src_dir):
        # Calculate total images for progress tracking
        total_images = sum(
            len([f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))])
            for _, _, files in os.walk(args.src_dir)
        )

        # Set progress bar description dynamically
        progress_desc = f"Saving {args.annotation_mode.capitalize()} annotations"

        # Initialize tqdm progress bar
        with tqdm(total=total_images, desc=progress_desc) as pbar:
            for root, _, files in os.walk(args.src_dir):
                # Filter valid image files
                valid_images = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))]
                if not valid_images:
                    continue

                # Define the output directory for annotations
                relative_path = os.path.relpath(root, args.src_dir)
                output_dir = os.path.join(args.dst_dir, relative_path)

                # Process each annotation mode
                if args.annotation_mode in ['labelme', 'all']:
                    for file in valid_images:
                        img_path = os.path.join(root, file)
                        annotator.save_labelme_annotation(
                            img_path, output_dir, conf=args.conf, move_images=args.move_images
                        )
                        pbar.update(1)

                if args.annotation_mode in ['yolo', 'all']:
                    annotator.save_yolo_annotations(root, output_dir, conf=args.conf, move_images=args.move_images)
                    pbar.update(len(valid_images))  # Update the progress bar for all images in the directory
    else:
        print(f"Error: {args.src_dir} is not a directory.")

    print("Processing complete.")



if __name__ == "__main__":
    main()
