"""models/configurations.py"""

# Imports
import torch
from detectron2.config import get_cfg
from detectron2 import model_zoo

# Configuration for Detectron2 Model
detectron_cfg = get_cfg()
#detectron_cfg.MODEL.WEIGHTS = "/model_0009999.pth" <= change this to your model path
detectron_cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_50_FPN_3x")
detectron_cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
detectron_cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.85
detectron_cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
