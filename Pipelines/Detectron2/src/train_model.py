from detectron2.utils.logger import setup_logger
setup_logger()
import os
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.data.datasets import register_coco_instances
from detectron2.engine import DefaultTrainer
from detectron2.evaluation import COCOEvaluator

register_coco_instances("my_dataset_train", {}, "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_coco/coco_train.json", "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_coco/train")
register_coco_instances("my_dataset_val", {}, "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_coco/coco_val.json", "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_coco/val")
register_coco_instances("my_dataset_test", {}, "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_coco/coco_test.json", "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_coco/test")




class CocoTrainer(DefaultTrainer):

  @classmethod
  def build_evaluator(cls, cfg, dataset_name, output_folder=None):

    if output_folder is None:
        os.makedirs("coco_eval", exist_ok=True)
        output_folder = "coco_eval"

    return COCOEvaluator(dataset_name, cfg, False, output_folder)



cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"))

# Basic configuration
cfg.DATASETS.TRAIN = ("my_dataset_train",)
cfg.DATASETS.TEST = ("my_dataset_val",)
cfg.DATALOADER.NUM_WORKERS = 4
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml")
cfg.SOLVER.IMS_PER_BATCH = 4
cfg.SOLVER.BASE_LR = 0.001

# Augmentation configuration (correct approach)
cfg.INPUT.CROP.ENABLED = True
cfg.INPUT.CROP.TYPE = "relative_range"
cfg.INPUT.CROP.SIZE = [0.8, 0.8]  # Random crop
cfg.INPUT.MIN_SIZE_TRAIN = 640  
cfg.INPUT.MAX_SIZE_TRAIN = 640
cfg.INPUT.RANDOM_FLIP = "horizontal"
cfg.INPUT.COLOR_AUGMENTATION = True  # Enables brightness/contrast/lighting

# Custom augmentation through config (no direct DatasetMapper assignment)
cfg.AUGMENTATIONS = [
    "RandomRotation", 
    "RandomBrightness", 
    "RandomContrast",
    "RandomLighting"
]

# Solver configuration
cfg.SOLVER.WARMUP_ITERS = 1000
cfg.SOLVER.MAX_ITER = 10000
cfg.SOLVER.STEPS = (3000, 4000)  # Should be within MAX_ITER
cfg.SOLVER.GAMMA = 0.05

# Model configuration
cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 64 
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
cfg.TEST.EVAL_PERIOD = 500

os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
trainer = CocoTrainer(cfg)
trainer.resume_or_load(resume=False)
trainer.train()