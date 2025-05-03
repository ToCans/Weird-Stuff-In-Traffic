import os
import cv2
import numpy as np
from PIL import Image
import random
import json

input_dir = 'clean_images'
mask_dir = 'masks'

os.makedirs(mask_dir, exist_ok=True)

# Load configuration from JSON file
with open('gen_config.json', 'r') as f:
    config = json.load(f)

# Settings from config
insert_box_width_ratio = config['insert_box_width_ratio']
insert_box_height_ratio = config['insert_box_height_ratio']
position_variation_ratio = config['position_variation_ratio']
dim_variation_ratio = config['dim_variation_ratio']

for img_name in os.listdir(input_dir):
    if not img_name.lower().endswith(('.jpg', '.png')):
        continue

    img_path = os.path.join(input_dir, img_name)
    img = Image.open(img_path)
    img_width, img_height = img.size

    # Insert Box Size with Variation
    box_w = int(img_width * insert_box_width_ratio)
    box_h = int(img_height * insert_box_height_ratio)

    dw = int(box_w * dim_variation_ratio)
    dh = int(box_h * dim_variation_ratio)

    box_w += random.randint(-dw, dw)
    box_h += random.randint(-dh, dh)

    box_w = max(int(img_width * 0.05), min(box_w, int(img_width * 0.4)))
    box_h = max(int(img_height * 0.05), min(box_h, int(img_height * 0.4)))

    # Position Variation
    max_dx = int(img_width * position_variation_ratio)
    max_dy = int(img_height * position_variation_ratio)

    dx = random.randint(-max_dx, max_dx)
    dy = random.randint(-max_dy, max_dy)

    # Insert Box Position (centered with variation)
    x1 = int((img_width - box_w) / 2) + dx
    y1 = int((img_height - box_h) / 1.5) + dy

    # Ensure within image bounds
    x1 = max(0, min(x1, img_width - box_w))
    y1 = max(0, min(y1, img_height - box_h))

    x2 = x1 + box_w
    y2 = y1 + box_h

    # Create mask
    mask = np.zeros((img_height, img_width), dtype=np.uint8)
    cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)

    mask_path = os.path.join(mask_dir, img_name.replace('.jpg', '.png').replace('.jpeg', '.png'))
    cv2.imwrite(mask_path, mask)

print("\n✅ Alle Masken erfolgreich mittig mit Positions- und Größenvariation erstellt und gespeichert.")
