# Object Detection Pipelines

This repository contains multiple object detection pipelines using **Detectron2** and **YOLO**, each organized by directory with relevant scripts for training, annotation, visualization, and evaluation.

---

## 📁 Project Structure

### `Detectron2/`

A pipeline for object detection using Facebook AI's Detectron2.

**Main Scripts:**
- `confusion_matrix.py` — Generates the confusion matrix.
- `optuna_model_organization.py` — Performs hyperparameter tuning using Optuna.
- `predictions.py` — Visualizes predictions made by the Detectron2 model.
- `train_model.py` — Trains the Detectron2 model.

**Utilities (`src/utils/`):**
- `auto_annotation_detectron2.py` — Helps with semi-automatic image annotation.
- `coco_visualization.py` — Visualizes COCO-style annotations on images.
- `CovertAnnotations_YOLO_to_COCO_format.ipynb` — Converts YOLO annotations to COCO JSON format.
- `delete_unpaired_files.py` — Deletes images with no annotations and vice versa.
- `obj.names` — List of class names used during annotation conversion.
- `png2jpg.py` — Converts PNG images to JPEG.
- `resize_image.py` — Resizes images to multiple target sizes.

---

### `yolo-object-detection/`

YOLO-based object detection pipeline with training, tuning, and visualization support.

**Scripts:**
- `annotations_visualization.py` — Visualizes annotations on images.
- `auto_annotations.py` — Assists with semi-automatic annotation of new data.
- `best.pt` — Best performing Yolo11n model.
- `data.yaml`, `data_tune.yaml` — Dataset configuration files for training and tuning.
- `inference.py` — Visualizes YOLO model predictions, with options to save the bounding boxes and annotated images.
- `train.py` — Trains the YOLO model.
- `tune.py` — Performs hyperparameter tuning for the YOLO model using Optuna.
- `train_best_trials.py` — Trains the YOLO model with hyperparameters from the best trial(s) in the .db file.
- `yolo_optuna_11n.db` — Optuna study containing all runs and results
- `yolo_version_benchmarking.py` — Benchmarks different YOLO versions (e.g. v8s, v11n..) on different subsets of the dataset
- `agg_benchmark_results.py` — Aggregates the results of all benchmarking runs 

---

### `yolo-street-detection/`

Specialized YOLO pipeline for street-level object detection.

**Main Script:**
- `main.py` — Entry point for starting the training pipeline.

**Library (`lib/`):**
- `_init_.py`
- `imports.py` — Contains import logic for the YOLO modules.
- `misc.py` — Miscellaneous helper functions for the training pipeline.

**Models (`models/`):**
- `streetseg_256_auto.pt` — Fine-tuned YOLO model.
- `yolo11s-seg.pt` — Pre-trained base model.

**Validation (`validation/`):**
- `yolo_street_detection_validation.ipynb` — Jupyter notebook for model validation.

---

## 📌 Notes

- All training scripts assume proper dataset structure and configuration.
- Ensure dependencies such as Detectron2, PyTorch, and YOLO libraries are installed.
- Configuration files (`.yaml`) should be updated with correct dataset paths.
