import os
import random
import requests
import json
import base64
import cv2
from PIL import Image
import io

input_dir = 'clean_images'
mask_dir = 'masks'
output_weird = 'dataset/weird'
output_labels = 'dataset/labels'
resize_target = (640, 640)

os.makedirs(output_weird, exist_ok=True)
os.makedirs(output_labels, exist_ok=True)

with open('gen_config.json', 'r') as f:
    config = json.load(f)

with open('prompts/train_objects.txt', 'r') as f:
    prompt_objects = [line.strip() for line in f if line.strip()]

extra_attributes = [
    "realistic texture", "photorealistic material", "perfect shadows",
    "urban fitting style", "complex surface", "high quality material",
    "integrated into street scene"
]

banned_words = ["giant", "huge", "massive", "enormous"]

def clean_prompt(prompt):
    for word in banned_words:
        prompt = prompt.replace(word, "")
    return prompt.strip()

def img_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def generate_prompt():
    obj = random.choice(prompt_objects)
    extras = ", ".join(random.sample(extra_attributes, 3))
    full_prompt = f"{config['prompt_prefix']} {obj}, {extras}, highly detailed, photorealistic, HDR, cinematic lighting, urban street scene"
    return clean_prompt(full_prompt)

def generate_weird(clean_path, mask_path, output_img, label_path):
    prompt = generate_prompt()

    img_pil = Image.open(clean_path)
    img_width, img_height = img_pil.size

    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    cv2.imwrite('temp_mask.png', mask)

    payload = {
        "init_images": [img_to_base64(clean_path)],
        "mask": img_to_base64('temp_mask.png'),
        "prompt": prompt,
        "negative_prompt": "low quality, blurry, grey blob, bad anatomy, unrecognizable, incomplete object",
        "denoising_strength": 0.75,
        "cfg_scale": 10,
        "steps": 40,
        "sampler_name": "DPM++ 2M Karras",
        "width": img_width,
        "height": img_height,
        "inpaint_full_res": True,
        "inpainting_fill": 1,
        "inpaint_full_res_padding": 64,
        "mask_blur": 4
    }

    try:
        r = requests.post("http://127.0.0.1:7860/sdapi/v1/img2img", json=payload)
        result = r.json()['images'][0]
        img_data = base64.b64decode(result)
        img = Image.open(io.BytesIO(img_data))
        img.resize(resize_target, Image.LANCZOS).save(output_img)

        x, y, w, h = cv2.boundingRect(mask)
        padding = 50
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(img_width - x, w + padding * 2)
        h = min(img_height - y, h + padding * 2)

        x_center = (x + w / 2) / img_width
        y_center = (y + h / 2) / img_height
        norm_w = w / img_width
        norm_h = h / img_height

        with open(label_path, 'w') as f:
            f.write(f"0 {x_center:.6f} {y_center:.6f} {norm_w:.6f} {norm_h:.6f}")

    except Exception as e:
        print(f"[ERROR] Failed on {clean_path}: {e}")

# Main loop
images = [img for img in os.listdir(input_dir) if img.endswith(('.jpg', '.png'))]

for img in images:
    clean_path = os.path.join(input_dir, img)
    mask_path = os.path.join(mask_dir, img.replace('.jpg', '.png').replace('.jpeg', '.png'))
    output_img = os.path.join(output_weird, img)
    label_path = os.path.join(output_labels, img.replace('.jpg', '.txt').replace('.png', '.txt'))

    if not os.path.exists(output_img):
        generate_weird(clean_path, mask_path, output_img, label_path)
    else:
        print(f"[SKIP] Already exists: {img}")