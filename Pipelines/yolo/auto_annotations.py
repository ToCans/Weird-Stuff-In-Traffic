import os
import shutil
import cv2
from pathlib import Path
from ultralytics import YOLO
from tqdm import tqdm


def run_detection(model, image_paths):
    return [model(path) for path in image_paths]


def export_yolo_format(model, source_dir, target_dir, conf_threshold, copy_images=False):
    os.makedirs(target_dir, exist_ok=True)
    image_list = [img for img in os.listdir(source_dir) if img.lower().endswith(('.jpg', '.jpeg', '.png'))]

    if not image_list:
        return

    for img_name in image_list:
        full_img_path = os.path.join(source_dir, img_name)
        image = cv2.imread(full_img_path)

        if image is None:
            print(f"Warning: could not read image: {full_img_path}")
            continue

        detections = model(image, conf=conf_threshold, verbose=False)
        label_path = os.path.join(target_dir, f"{Path(img_name).stem}.txt")

        with open(label_path, 'w') as out_file:
            if detections and detections[0].boxes:
                boxes = detections[0].boxes
                for (bbox, cls_id) in zip(boxes.xywhn.cpu().numpy(), boxes.cls.cpu().numpy()):
                    xc, yc, w, h = bbox[:4]
                    out_file.write(f"{int(cls_id)} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")

        if copy_images:
            shutil.copy(full_img_path, os.path.join(target_dir, img_name))


# Example usage:
model_path = "path/to/your/model.pt"  
model = YOLO(model_path)
image_path = "path/to/your/images"
output_path = "path/to/output"
conf_threshold = 0.5
export_yolo_format(model, source_dir=image_path, target_dir=output_path, conf_threshold=conf_threshold, copy_images=True)
