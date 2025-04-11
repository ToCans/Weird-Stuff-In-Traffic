
from ultralytics import YOLO

# Load a model
model = YOLO("/home/daniel/projects/yolo_motion_detection/yolo11n.pt")  # load a pretrained model (recommended for training)

# Train the model
results = model.train(data="/dataset.yaml",
                      epochs=100,
                      imgsz=128,
                      batch=128,
                      name="",
                      cache="disk",
                      resume=False,
                      model="yolov11n.pt",
                      task="detect",
                      device=0
                      )


