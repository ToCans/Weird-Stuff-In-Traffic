"""models/configurations.py"""

# Imports
import torch
import os
import re
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.data import MetadataCatalog

# Current Directory Setup
current_directory = os.getcwd()
path_to_base_directory = re.search(rf"(.*?){"Weird-Stuff-In-Traffic"}", current_directory).group(1)

test_metadata = MetadataCatalog.get("my_dataset_test")
test_metadata.thing_classes = [""] 

# Configuration for Detectron2 Model
detectron_cfg = get_cfg()
detectron_cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"))
detectron_cfg.MODEL.WEIGHTS = path_to_base_directory+"/Weird-Stuff-In-Traffic/App/Backend/models/detectron2_best.pth"
detectron_cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
detectron_cfg.DATASETS.TEST = ("my_dataset_test", )

detectron_cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.80
detectron_cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
