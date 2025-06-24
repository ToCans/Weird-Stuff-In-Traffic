from detectron2.utils.logger import setup_logger
setup_logger()
import os
import optuna
from optuna.samplers import TPESampler
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.data import build_detection_train_loader, DatasetMapper
from detectron2.data.datasets import register_coco_instances
from detectron2.engine import DefaultTrainer
from detectron2.evaluation import COCOEvaluator
import detectron2.data.transforms as T
from datetime import datetime
# Dataset Paths
DATASET_PATHS = {
    "train": ("/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/coco_datasets/train_annotations.json",
              "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/coco_datasets/train"),
    "val": ("/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/coco_datasets/val_annotations.json",
            "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/coco_datasets/val")
}

# Register datasets
register_coco_instances("my_dataset_train", {}, *DATASET_PATHS["train"])
register_coco_instances("my_dataset_val", {}, *DATASET_PATHS["val"])

class CocoTrainer(DefaultTrainer):
    @classmethod
    def build_evaluator(cls, cfg, dataset_name, output_folder=None):
        if output_folder is None:
            os.makedirs("coco_eval", exist_ok=True)
            output_folder = "coco_eval"
        return COCOEvaluator(dataset_name, cfg, False, output_folder)


def build_augmentations(trial):
    augmentations = []

    if trial.suggest_categorical("use_flip", [True, False]):
        flip_horizontal = trial.suggest_categorical("flip_horizontal", [True, False])
        flip_vertical = trial.suggest_categorical("flip_vertical", [True, False])

        flip_prob = trial.suggest_float("flip_prob", 0.0, 1.0)

        if not flip_horizontal and not flip_vertical:
            flip_horizontal = True  # default to something valid

        if flip_horizontal:
            augmentations.append(T.RandomFlip(horizontal=True, vertical=False, prob=flip_prob))

        if flip_vertical:
            augmentations.append(T.RandomFlip(horizontal=False, vertical=True, prob=flip_prob))

    if trial.suggest_categorical("use_brightness", [True, False]):
        augmentations.append(T.RandomBrightness(
            trial.suggest_float("brightness_min", 0.7, 1.0),
            trial.suggest_float("brightness_max", 1.0, 1.3)
        ))

    if trial.suggest_categorical("use_contrast", [True, False]):
        augmentations.append(T.RandomContrast(
            trial.suggest_float("contrast_min", 0.7, 1.0),
            trial.suggest_float("contrast_max", 1.0, 1.3)
        ))

    if trial.suggest_categorical("use_saturation", [True, False]):
        augmentations.append(T.RandomSaturation(
            trial.suggest_float("saturation_min", 0.7, 1.0),
            trial.suggest_float("saturation_max", 1.0, 1.3)
        ))

    if trial.suggest_categorical("use_rotation", [True, False]):
        angle_min = trial.suggest_int("rotation_min", -30, -5)
        angle_max = trial.suggest_int("rotation_max", 5, 30)
        augmentations.append(T.RandomRotation(angle=[angle_min, angle_max]))

    return augmentations


def objective(trial):
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"))
    
    # Hyperparameters with optimized search spaces
    cfg.SOLVER.BASE_LR = trial.suggest_float("BASE_LR", 1e-5, 0.001, log=True)
    cfg.SOLVER.OPTIMIZER = trial.suggest_categorical('optimizer', ['ADAMW', 'SGD']) 
    cfg.SOLVER.WEIGHT_DECAY = trial.suggest_float('weight_decay', 1e-5, 0.001, log=True)
    
    cfg.AUGMENTATIONS = build_augmentations(trial)
    
    # Optimizer-specific parameters
    if cfg.SOLVER.OPTIMIZER == "SGD":
        cfg.SOLVER.MOMENTUM = trial.suggest_float("MOMENTUM", 0.88, 0.95)
        cfg.SOLVER.NESTEROV = trial.suggest_categorical('nesterov', [True, False])
    elif cfg.SOLVER.OPTIMIZER == "ADAMW":
        cfg.SOLVER.BETAS = (
            trial.suggest_float("BETA1", 0.85, 0.99),
            trial.suggest_float("BETA2", 0.9, 0.999)
        )
    
    # Batch and workers
    cfg.SOLVER.IMS_PER_BATCH = trial.suggest_categorical("IMS_PER_BATCH", [1, 2])  
    cfg.DATALOADER.NUM_WORKERS = 8
    
    # Enhanced learning rate schedule
    cfg.SOLVER.GAMMA = trial.suggest_float("GAMMA", 0.15, 0.3)
    lr_scheduler = trial.suggest_categorical("lr_scheduler", ["step", "cosine"])
    
    if lr_scheduler == "step":
        step_patterns = {
            "early": (1000, 2000, 3000),
            "mid": (1500, 3000, 4500),
            "late": (2000, 3500, 4000)
        }
        selected_steps = trial.suggest_categorical("step_pattern", list(step_patterns.keys()))
        cfg.SOLVER.STEPS = step_patterns[selected_steps]
        cfg.SOLVER.MAX_ITER = 6000
    else:  # cosine
        cfg.SOLVER.MAX_ITER = 6000
    
    # Image configuration
    cfg.INPUT.MIN_SIZE_TRAIN = trial.suggest_categorical("MIN_SIZE_TRAIN", [640, 800, 896])
    cfg.INPUT.MAX_SIZE_TRAIN = trial.suggest_categorical("MAX_SIZE_TRAIN", [640, 1333, 1600])

    cfg.INPUT.MIN_SIZE_TRAIN_SAMPLING = trial.suggest_categorical("size_sampling", ["choice", "range"])
    
    # Model parameters
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml")
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = trial.suggest_categorical("roi_batch_size", [64, 96, 128])
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1

    # ===== Enhanced Anchor Configuration =====
    cfg.MODEL.ANCHOR_GENERATOR.SIZES = [[8, 16, 32, 64, 128, 256, 512, 1024]]
    cfg.MODEL.ANCHOR_GENERATOR.ASPECT_RATIOS = [[0.25, 0.5, 1.0, 2.0, 4.0]]  
    cfg.MODEL.RPN.IN_FEATURES = ["p2", "p3", "p4", "p5", "p6"]  

    cfg.MODEL.RPN.PRE_NMS_TOPK_TRAIN = trial.suggest_int("rpn_pre_nms_topk_train", 2000, 20000, step=1000)
    cfg.MODEL.RPN.POST_NMS_TOPK_TRAIN = trial.suggest_int("rpn_post_nms_topk_train", 1000, 5000, step=500)
        


    
    # Training parameters
    cfg.TEST.EVAL_PERIOD = 500
    cfg.SOLVER.WARMUP_ITERS = trial.suggest_int("warmup_iters", 500, 2000, step=500)
    cfg.SOLVER.CHECKPOINT_PERIOD = 500
    cfg.DATASETS.TRAIN = ("my_dataset_train",)
    cfg.DATASETS.TEST = ("my_dataset_val",)
    
    # Output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cfg.OUTPUT_DIR = f"./output/trial_{trial.number}_{timestamp}"
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    
    # Training
    trainer = CocoTrainer(cfg)
    trainer.resume_or_load(resume=False)
    trainer.train()
    
    # Evaluation
    val_results = trainer.test(cfg, trainer.model)
    return val_results["bbox"]["AP"]

if __name__ == "__main__":
    study = optuna.create_study(
        direction="maximize",
        sampler=TPESampler(n_startup_trials=20),
        pruner=optuna.pruners.HyperbandPruner(
            min_resource=1000,
            max_resource=5000,
            reduction_factor=3
        ),
        storage="sqlite:///detectron2_optuna_full.db",
        study_name="detectron2_full_tuning",
        load_if_exists=True
    )
    
    try:
        study.optimize(objective, n_trials=200, timeout=144 * 60 * 60)  # 144 hours = 6 days
    except KeyboardInterrupt:
        print("Optimization stopped by user")

    
    # Results and config saving (same as before)
    print("\nBest trial:")
    trial = study.best_trial
    print(f"  AP: {trial.value:.4f}")
    print("  Parameters:")
    for key, value in trial.params.items():
        print(f"    {key}: {value}")
    
    best_cfg = get_cfg()
    best_cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"))
    for key, value in trial.params.items():
        if hasattr(best_cfg.SOLVER, key):
            setattr(best_cfg.SOLVER, key, value)
    
    with open("best_config_full.yaml", "w") as f:
        f.write(best_cfg.dump())

