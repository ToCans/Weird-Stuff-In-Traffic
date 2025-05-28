import os
import json
import cv2
import torch
from tqdm import tqdm
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.data import MetadataCatalog
from detectron2.structures import BoxMode

# === CONFIGURATION ===
IMAGE_DIR = "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/raw_datasets/20250528_dataset/annotation_images_shaquille"
OUTPUT_JSON = "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/raw_datasets/20250528_dataset/auto_annotations.json"
MODEL_WEIGHTS = "/home/danielshaquille/Daniel/projects/code/weird_stuff_in_traffic_local/output/20250526_ws_best_model.pth"
DATASET_NAME = "inference_dataset"

# === SETUP DETECTRON2 MODEL ===
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"))
cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
cfg.MODEL.WEIGHTS = MODEL_WEIGHTS
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.85
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
predictor = DefaultPredictor(cfg)

# === GET METADATA & CLASSES ===
# Register dummy dataset to enable class name retrieval
MetadataCatalog.get(DATASET_NAME).thing_classes = ["weird_object"]  # Insert class names here
class_names = MetadataCatalog.get(DATASET_NAME).thing_classes

# === PREPARE COCO STRUCTURE ===
coco_output = {
    "images": [],
    "annotations": [],
    "categories": [
        {"id": idx, "name": name, "supercategory": "none"}
        for idx, name in enumerate(class_names)
    ]
}

# === PROCESS IMAGES ===
image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
annotation_id = 1

for image_id, filename in enumerate(tqdm(image_files)):
    filepath = os.path.join(IMAGE_DIR, filename)
    image = cv2.imread(filepath)
    height, width = image.shape[:2]

    # COCO image record
    coco_output["images"].append({
        "id": image_id,
        "width": width,
        "height": height,
        "file_name": filename,
        "folder": IMAGE_DIR,
        "depth": 3
    })

    # Predict
    outputs = predictor(image)
    instances = outputs["instances"].to("cpu")

    for i in range(len(instances)):
        box = instances.pred_boxes[i].tensor.numpy()[0]  # [x1, y1, x2, y2]
        score = float(instances.scores[i])
        category_id = int(instances.pred_classes[i].item())

        x, y, x2, y2 = box
        bbox = [float(x), float(y), float(x2 - x), float(y2 - y)]  # COCO format

        annotation = {
            "id": annotation_id,
            "image_id": image_id,
            "category_id": category_id,
            "bbox": bbox,
            "area": float(bbox[2] * bbox[3]),
            "iscrowd": 0,
            "segmentation": [],
            "score": score
        }
        coco_output["annotations"].append(annotation)
        annotation_id += 1

# === SAVE TO JSON ===
with open(OUTPUT_JSON, 'w') as f:
    json.dump(coco_output, f, indent=2)

print(f"\nAuto-annotations saved to: {OUTPUT_JSON}")
