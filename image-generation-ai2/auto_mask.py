import os
import cv2
import numpy as np
from PIL import Image
import random

input_dir = 'clean_images'
mask_dir = 'masks'

os.makedirs(mask_dir, exist_ok=True)

# Einstellungen
insert_box_width_ratio = 0.15  # Basis: 20% der Bildbreite
insert_box_height_ratio = 0.15  # Basis: 20% der Bildhöhe
position_variation_ratio = 0.1  # max 10% Positionsabweichung
dim_variation_ratio = 0.05  # max 10% Größenabweichung

for img_name in os.listdir(input_dir):
    if not img_name.lower().endswith(('.jpg', '.png')):
        continue

    img_path = os.path.join(input_dir, img_name)
    img = Image.open(img_path)
    img_width, img_height = img.size

    # Insert Box Size mit Variation
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

    # Insert Box Position (zentriert mit Variation)
    x1 = int((img_width - box_w) / 2) + dx
    y1 = int((img_height - box_h) / 1.5) + dy

    # Begrenzung innerhalb des Bildes
    x1 = max(0, min(x1, img_width - box_w))
    y1 = max(0, min(y1, img_height - box_h))

    x2 = x1 + box_w
    y2 = y1 + box_h

    # Maske erstellen
    mask = np.zeros((img_height, img_width), dtype=np.uint8)
    cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)

    mask_path = os.path.join(mask_dir, img_name.replace('.jpg', '.png').replace('.jpeg', '.png'))
    cv2.imwrite(mask_path, mask)

print("\n✅ Alle Masken erfolgreich mittig mit Positions- und Größenvariation erstellt und gespeichert.")
