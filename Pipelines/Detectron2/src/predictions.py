import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()
import cv2
import random
import os
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
from detectron2.data.datasets import register_coco_instances
import torch
from IPython.display import display
import PIL
import glob
import time

# Register dataset
register_coco_instances("my_dataset_test", {}, 
                      "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_coco/coco_test.json",
                      "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_coco/test")
test_metadata = MetadataCatalog.get("my_dataset_test")
test_metadata.thing_classes = ["weird_object"]  # Since you have NUM_CLASSES = 1

# Configuration
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"))
cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
cfg.MODEL.WEIGHTS = "/home/danielshaquille/Daniel/projects/code/weird_stuff_in_traffic/output/model_0009999.pth"
cfg.DATASETS.TEST = ("my_dataset_test", )
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.85
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
predictor = DefaultPredictor(cfg)

# Image settings
TARGET_WIDTH = 640
TARGET_HEIGHT = 640
OUTPUT_DIR = "/home/danielshaquille/Daniel/projects/code/weird_stuff_in_traffic/predictions"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Get images
all_images = glob.glob('/home/danielshaquille/Daniel/projects/datasets/weird_stuff_coco/test/*jpg')

# Select random images
random.seed(20)
selected_images = random.sample(all_images, min(5, len(all_images)))

# For timing (in milliseconds)
inference_times_ms = []

# First run - warm up only
if len(selected_images) > 0:
    warm_up_image = selected_images[0]
    im = cv2.imread(warm_up_image)
    resized_im = cv2.resize(im, (TARGET_WIDTH, TARGET_HEIGHT))
    start_time = time.time()
    _ = predictor(resized_im)
    warmup_time = (time.time() - start_time) * 1000
    print(f"Warm-up run completed in {warmup_time:.2f} ms (discarded from averages)\n")

# Process all images (including first one)
for i, image_path in enumerate(selected_images):
    # Read and resize image
    im = cv2.imread(image_path)
    resized_im = cv2.resize(im, (TARGET_WIDTH, TARGET_HEIGHT))
    
    # Time inference
    start_time = time.time()
    outputs = predictor(resized_im)
    inference_time_ms = (time.time() - start_time) * 1000
    
    # Store timing (skip first image for metrics)
    if i > 0:
        inference_times_ms.append(inference_time_ms)
    
    # Visualize predictions
    v = Visualizer(resized_im[:, :, ::-1],
                 metadata=test_metadata,
                 scale=1.0,
                 instance_mode=detectron2.utils.visualizer.ColorMode.IMAGE)
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    visualized_image = out.get_image()[:, :, ::-1]
    
    # Save visualization
    filename = os.path.basename(image_path)
    output_path = os.path.join(OUTPUT_DIR, f"pred_{filename}")
    cv2.imwrite(output_path, visualized_image)
    
    # Display
    display(PIL.Image.fromarray(visualized_image[..., ::-1]))
    print(f"Image {i+1}/{len(selected_images)}: {filename}")
    print(f"Inference time: {inference_time_ms:.2f} ms")
    print(f"Saved to: {output_path}\n")

# Performance metrics (excluding warm-up)
if inference_times_ms:
    avg_time_ms = sum(inference_times_ms) / len(inference_times_ms)
    min_time_ms = min(inference_times_ms)
    max_time_ms = max(inference_times_ms)
    
    print("\nPerformance Metrics (excluding first warm-up run):")
    print(f"Number of measured runs: {len(inference_times_ms)}")
    print(f"Average inference time: {avg_time_ms:.2f} ms")
    print(f"Minimum inference time: {min_time_ms:.2f} ms")
    print(f"Maximum inference time: {max_time_ms:.2f} ms")
    print(f"Total measured inference time: {sum(inference_times_ms):.2f} ms")
    print(f"FPS: {1000/avg_time_ms:.2f}")
else:
    print("\nNote: Only warm-up run completed (no performance metrics available)")