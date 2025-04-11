"""
Script name: Observing Yolo average inference time
File name: inference_time.py
Author: Daniel Shaquille
"""
import os
import cv2
import time
import argparse
from ultralytics import YOLO

def load_model(model_path):
    """Load the YOLO model in TensorRT engine format."""
    model = YOLO(model_path)  # Automatically detects and loads TensorRT engine or other model formats
    return model

def measure_inference_time(model, input_folder, imgsz, conf, device):
    """Measure inference time for all images in the input folder."""
    # Filter image files
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        print("No images found in the input folder.")
        return

    total_time = 0
    total_images = 0
    first_inference_done = False

    for i, image_file in enumerate(image_files):
        image_path = os.path.join(input_folder, image_file)

        # Read the image
        image = cv2.imread(image_path)

        if image is None:
            print(f"[{i}] {image_file} - Could not read image. Skipping...")
            continue

        # Perform prediction and measure time
        start_time = time.time()
        results = model.predict(image, imgsz=imgsz, conf=conf, device=device, verbose=False)
        inference_time = time.time() - start_time

        if not first_inference_done:
            print(f"[{i}] {image_file} - First inference time (not recorded): {inference_time * 1000:.2f} ms")
            first_inference_done = True
            continue

        total_time += inference_time
        total_images += 1

        print(f"[{i}] {image_file} - Inference time: {inference_time * 1000:.2f} ms")

    if total_images > 0:
        avg_time_ms = (total_time / total_images) * 1000
        print(f"\nProcessed {total_images} images (excluding the first inference).")
        print(f"Average inference time: {avg_time_ms:.2f} ms per image")
    else:
        print("No images processed.")

def main():
    parser = argparse.ArgumentParser(description="Measure inference time of a YOLO model.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the YOLO model (TensorRT or others).")
    parser.add_argument("--input_folder", type=str, required=True, help="Folder containing input images.")
    parser.add_argument("--imgsz", type=int, default=128, help="Image size for inference.")
    parser.add_argument("--conf", type=float, default=0.4, help="Confidence threshold for predictions.")
    parser.add_argument("--device", type=str, default="cuda:0", help="Device to run the inference (e.g., 'cuda:0').")
    args = parser.parse_args()

    # Load the model
    print(f"Loading model from {args.model_path}...")
    model = load_model(args.model_path)

    # Measure inference time
    measure_inference_time(model, args.input_folder, args.imgsz, args.conf, args.device)

if __name__ == "__main__":
    main()
