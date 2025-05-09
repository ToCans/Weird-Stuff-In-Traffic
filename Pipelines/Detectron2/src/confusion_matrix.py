from detectron2.utils.logger import setup_logger
setup_logger()
import numpy as np
import os
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
import torch
import supervision as sv



# Model configuration
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"))
cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  # Your actual class count
cfg.MODEL.WEIGHTS = "/home/danielshaquille/Daniel/projects/code/weird_stuff_in_traffic/output/model_0009999.pth"
predictor = DefaultPredictor(cfg)


# Key change: force_masks=False
dataset = sv.DetectionDataset.from_coco(
    images_directory_path="/home/danielshaquille/Daniel/projects/datasets/weird_stuff_coco/test",
    annotations_path="/home/danielshaquille/Daniel/projects/datasets/weird_stuff_coco/coco_test.json",
    force_masks=False  # Disable mask loading
)

def callback(image: np.ndarray) -> sv.Detections:
    result = predictor(image)
    detections = sv.Detections.from_detectron2(result)
    mask = detections.confidence >= 0.85
    return sv.Detections(
        xyxy=detections.xyxy[mask],
        confidence=detections.confidence[mask],
        class_id=detections.class_id[mask]
    )

confusion_matrix = sv.ConfusionMatrix.benchmark(dataset=dataset, callback=callback)
confusion_matrix.plot()

# Create output directory if it doesn't exist
output_dir = "/home/danielshaquille/Daniel/projects/code/weird_stuff_in_traffic/results"  # Change this to your desired path
os.makedirs(output_dir, exist_ok=True)

# Generate and save confusion matrix
confusion_matrix = sv.ConfusionMatrix.benchmark(dataset=dataset, callback=callback)
plot = confusion_matrix.plot()

# Save the plot to a file
output_path = os.path.join(output_dir, "confusion_matrix.png")
plot.savefig(output_path, bbox_inches='tight', dpi=300)
print(f"Confusion matrix saved to: {output_path}")

# Optionally display the image in notebook
# display(Image(filename=output_path))