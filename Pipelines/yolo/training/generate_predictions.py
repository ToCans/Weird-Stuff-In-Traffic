"""
Script name: Generate Yolo Predictions
File name: generate_predictions.py
Author: Daniel Shaquille
"""

import os
import cv2
import time
import argparse
from ultralytics import YOLO

def load_model(model_path):
    """Load YOLO model."""
    model = YOLO(model_path, task="detect")  # Load YOLO model (TensorRT format supported)
    return model

def perform_inference(model, input_folder, output_folder, imgsz, conf, device):
    """Perform inference on all images in the input folder."""
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Filter image files
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        print("No images found in the input folder.")
        return

    total_time = 0
    recorded_times = []

    for i, image_file in enumerate(image_files):
        image_path = os.path.join(input_folder, image_file)

        # Read image
        image = cv2.imread(image_path)

        if image is None:
            print(f"[{i}] {image_file} - Could not read image. Skipping...")
            continue

        # Perform prediction
        start_time = time.time()
        results = model.predict(image, imgsz=imgsz, conf=conf, device=device, verbose=False)
        inference_time = time.time() - start_time
        recorded_times.append(inference_time)

        print(f"[{i}] {image_file} - Inference time: {inference_time * 1000:.2f} ms")

        # Access and save predicted image
        pred_img = results[0].plot()  # Plot the predictions
        output_path = os.path.join(output_folder, f"pred_{image_file}")
        cv2.imwrite(output_path, pred_img)
        print(f"[{i}] {image_file} - Prediction saved to {output_path}")

    # Calculate and print average inference time, excluding the first time
    if len(recorded_times) > 1:
        avg_time_ms = (sum(recorded_times[1:]) / (len(recorded_times) - 1)) * 1000
        print(f"Average inference time (excluding first): {avg_time_ms:.2f} ms per image")
    else:
        print("No images processed or insufficient data for averaging.")

def main():
    parser = argparse.ArgumentParser(description="Perform inference using YOLO and save predictions.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the YOLO model.")
    parser.add_argument("--input_folder", type=str, required=True, help="Folder containing input images.")
    parser.add_argument("--output_folder", type=str, required=True, help="Folder to save predicted images.")
    parser.add_argument("--imgsz", type=int, default=128, help="Image size for inference.")
    parser.add_argument("--conf", type=float, default=0.4, help="Confidence threshold for predictions.")
    parser.add_argument("--device", type=str, default="cuda:0", help="Device to run inference (e.g., 'cuda:0').")
    args = parser.parse_args()

    # Load the YOLO model
    print(f"Loading model from {args.model_path}...")
    model = load_model(args.model_path)

    # Perform inference
    perform_inference(
        model,
        args.input_folder,
        args.output_folder,
        imgsz=args.imgsz,
        conf=args.conf,
        device=args.device,
    )

if __name__ == "__main__":
    main()



