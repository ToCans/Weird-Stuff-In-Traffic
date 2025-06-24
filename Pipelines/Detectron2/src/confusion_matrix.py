from detectron2.utils.logger import setup_logger
setup_logger()
import numpy as np
import pandas as pd
import seaborn as sns
import os
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
import torch
import supervision as sv
import matplotlib.pyplot as plt

conf_thr = 0.95
model_weights = "output/20250621_ws_best_model.pth"

# Create output directory if it doesn't exist
output_dir = "/home/danielshaquille/Daniel/projects/code/weird_stuff_in_traffic_local/results"

# Model configuration
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"))
cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 96
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  


 # ===== Enhanced Anchor Configuration =====
cfg.MODEL.ANCHOR_GENERATOR.SIZES = [[8, 16, 32, 64, 128, 256, 512, 1024]]
cfg.MODEL.ANCHOR_GENERATOR.ASPECT_RATIOS = [[0.25, 0.5, 1.0, 2.0, 4.0]]  
cfg.MODEL.RPN.IN_FEATURES = ["p2", "p3", "p4", "p5", "p6"]  

cfg.MODEL.RPN.PRE_NMS_TOPK_TRAIN = 12000
cfg.MODEL.RPN.POST_NMS_TOPK_TRAIN = 2500

cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = conf_thr
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1

cfg.MODEL.WEIGHTS = model_weights

predictor = DefaultPredictor(cfg)

dataset = sv.DetectionDataset.from_coco(
    images_directory_path="/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/coco_datasets/test",
    annotations_path="/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/coco_datasets/test_annotations.json",
    force_masks=False  
)



def callback(image: np.ndarray) -> sv.Detections:
    result = predictor(image)
    detections = sv.Detections.from_detectron2(result)
    mask = detections.confidence >= conf_thr
    return sv.Detections(
        xyxy=detections.xyxy[mask],
        confidence=detections.confidence[mask],
        class_id=detections.class_id[mask]
    )



os.makedirs(output_dir, exist_ok=True)

# Generate standard confusion matrix
confusion_matrix = sv.ConfusionMatrix.benchmark(dataset=dataset, callback=callback)
plot = confusion_matrix.plot()

# Save the standard plot
standard_output_path = os.path.join(output_dir, "confusion_matrix_standard.png")
plot.savefig(standard_output_path, bbox_inches='tight', dpi=300)


print(f"Confidence Threshold: {conf_thr}")

# Print original matrix
print("\nOriginal Matrix:")
print(confusion_matrix.matrix)



# Normalization
matrix = confusion_matrix.matrix.astype(float)
row_sums = matrix.sum(axis=1, keepdims=True)
normalized_matrix = np.divide(matrix, row_sums, where=row_sums!=0)
normalized_matrix = np.round(normalized_matrix, 4).round(2)

print("\nNormalized Matrix:")
print(normalized_matrix)

detectron_classes = ', '.join(confusion_matrix.classes)


# Create Seaborn plot
plt.figure(figsize=(8, 6))
class_names = [detectron_classes, "Background"]  # Add background class label
# Create DataFrame for better labeling
df_cm = pd.DataFrame(
    normalized_matrix,
    index=class_names,
    columns=class_names
)

heatmap = sns.heatmap(df_cm, annot=True, fmt=".2f", cmap="Blues", 
                     cbar=False, linewidths=0.5, linecolor="black")

plt.title("Normalized Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.yticks(rotation=0)

os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "normalized_confusion_matrix.png")
plt.savefig(output_path, bbox_inches='tight', dpi=300)
plt.close()

print(f"Seaborn confusion matrix saved to: {output_path}")
