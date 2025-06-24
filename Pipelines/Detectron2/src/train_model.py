from detectron2.utils.logger import setup_logger
setup_logger()
import os
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.data.datasets import register_coco_instances
from detectron2.engine import DefaultTrainer
from detectron2.evaluation import COCOEvaluator
import detectron2.data.transforms as T

register_coco_instances("my_dataset_train", {}, "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/coco_datasets/train_annotations.json", "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/coco_datasets/train")
register_coco_instances("my_dataset_val", {}, "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/coco_datasets/val_annotations.json", "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/coco_datasets/val")

class CocoTrainer(DefaultTrainer):
    @classmethod
    def build_evaluator(cls, cfg, dataset_name, output_folder=None):
        if output_folder is None:
            os.makedirs("coco_eval", exist_ok=True)
            output_folder = "coco_eval"
        return COCOEvaluator(dataset_name, cfg, False, output_folder)

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"))

# ===== Hyperparameters =====
cfg.SOLVER.BASE_LR = 0.000999522608518938
cfg.SOLVER.OPTIMIZER = "SGD"
cfg.SOLVER.MOMENTUM = 0.9466068689264724
cfg.SOLVER.NESTEROV = True
cfg.SOLVER.BETAS = (0.877647954779517, 0.973326758155428)
cfg.SOLVER.GAMMA = 0.2256106823389289
cfg.SOLVER.WEIGHT_DECAY = 0.00010461595069338793
cfg.SOLVER.IMS_PER_BATCH = 2
cfg.DATALOADER.NUM_WORKERS = 16
cfg.SOLVER.MAX_ITER = 15000
cfg.SOLVER.STEPS = (2000, 3500, 4000)  # Added learning rate drops
cfg.SOLVER.WARMUP_ITERS = 1000


# ===== Enhanced Anchor Configuration =====
cfg.MODEL.ANCHOR_GENERATOR.SIZES = [[8, 16, 32, 64, 128, 256, 512, 1024]]
cfg.MODEL.ANCHOR_GENERATOR.ASPECT_RATIOS = [[0.25, 0.5, 1.0, 2.0, 4.0]]  
cfg.MODEL.RPN.IN_FEATURES = ["p2", "p3", "p4", "p5", "p6"]  



# ===== Image Size =====
cfg.INPUT.MIN_SIZE_TRAIN = 800
cfg.INPUT.MAX_SIZE_TRAIN = 1600

# RPN Adjustments
cfg.MODEL.RPN.PRE_NMS_TOPK_TRAIN = 12000  
cfg.MODEL.RPN.POST_NMS_TOPK_TRAIN = 2500  



# Model Configuration
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml")
cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 96
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1




# ===== Augmentation =====
cfg.AUGMENTATIONS = [
    T.RandomRotation(angle=[-17, 23])
]

# Evaluation Configuration
cfg.TEST.EVAL_PERIOD = 500
cfg.SOLVER.CHECKPOINT_PERIOD = 500
cfg.DATASETS.TRAIN = ("my_dataset_train",)
cfg.DATASETS.TEST = ("my_dataset_val",)

# Output Directory
os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

# Start Training
trainer = CocoTrainer(cfg)
trainer.resume_or_load(resume=False)
trainer.train()