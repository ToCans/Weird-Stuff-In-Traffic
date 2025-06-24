Detectron2/
└── src/
    ├── confusion_matrix.py                                 # Generates the confusion matrix
    ├── optuna_model_organization.py                        # Run hyperparameter tuning on the Detectron2 model
    ├── predictions.py                                      # Visualize Detectron2 predictions
    ├── train_model.py                                      # script to train our model
    └── utils/
        ├── auto_annotation_detectron2.py                   # semi-auto annotations to help annotating new images
        ├── coco_visualization.py                           # visualize the annotations on the images
        ├── CovertAnnotations_YOLO_to_COCO_format.ipynb     # convert the yolo annotation format to coco json format
        ├── delete_unpaired_files.py                        # delete images containing no annotations and vice versa
        ├── obj.names                                       # class names for the yolo to coco annoatation conversion script
        ├── png2jpg.py                                      # convert png formatted images to jpeg format                                 
        └── resize_image.py                                 # Resize our image datasets to multiple size


yolo-object-detection/
├── annotations_visualization.py                            # visualize the annotations on the images
├── auto_annotations.py                                     # semi-auto annotations to help annotating new images
├── data_tune.yaml                                          # path of the dataset split
├── data.yaml                                               # path of the dataset split
├── inference.py                                            # Visualize YOLO predictions
├── train.py                                                # script to train our model
└── tune.py                                                 # Run hyperparameter tuning on the YOLO model

yolo-street-detection/
└── main.py                                                 # Starting the training pipeline
└── lib/
    ├── _init_.py                                           
    ├── imports.py                                          # Imports for yolo
    └── misc.py                                             # Training pipeline
└── models/
    ├── streetseg_256_auto.pt                               # Fine-tuned model
    └── yolo11s-seg.pt                                      # Pre-trained model
└── validation/                                 
        └── yolo_street_detection_validation.ipynb          # Validation script