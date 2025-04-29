import os
import random
import shutil
import requests
import json
import base64
import cv2
from PIL import Image
from sklearn.model_selection import train_test_split
import io

input_dir = 'clean_images'
mask_dir = 'masks'
output_base = 'dataset'
label_dir = 'labels'

split_ratio = [1, 0, 0]  # train, val, test
random.seed(42)

with open('gen_config.json', 'r') as f:
    config = json.load(f)

prompt_files = {
    'train': 'prompts/train_objects.txt',
    'val': 'prompts/train_objects.txt',
    'test': 'prompts/test_objects.txt'
}

resize_target = (640, 640)

fail_log = open('failed_prompts.log', 'w')

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

def generate_prompt(split_name):
    with open(prompt_files[split_name], 'r') as f:
        objects = f.readlines()
    prompt_object = random.choice(objects).strip()
    extras = ", ".join(random.sample(extra_attributes, 3))
    full_prompt = f"{config['prompt_prefix']} {prompt_object}, {extras}, highly detailed, photorealistic, HDR, cinematic lighting, urban street scene, sharp focus, complex shadows"
    full_prompt = clean_prompt(full_prompt)
    return full_prompt

def generate_weird(clean_path, mask_path, weird_path, label_path, split_name):
    full_prompt = generate_prompt(split_name)

    # Load original image
    img_pil = Image.open(clean_path)
    img_width, img_height = img_pil.size

    # Load and resize mask to original image size
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

    temp_mask_path = 'temp_mask.png'
    cv2.imwrite(temp_mask_path, mask)

    payload = {
        "init_images": [img_to_base64(clean_path)],
        "mask": img_to_base64(temp_mask_path),
        "prompt": full_prompt,
        "negative_prompt": "low quality, blurry, grey blob, bad anatomy, bad composition, deformed, unrecognizable, amorphous, extra limbs, incomplete object, unclear structure",
        "denoising_strength": 0.75,
        "cfg_scale": 10,
        "steps": 40,
        "sampler_name": "DPM++ 2M Karras",
        "width": img_width,
        "height": img_height,
        "mask_blur": 4,
        "inpainting_fill": 1,
        "inpaint_full_res": True,
        "inpaint_full_res_padding": 64,
        "restore_faces": False
    }

    try:
        response = requests.post("http://127.0.0.1:7860/sdapi/v1/img2img", json=payload)
        result = response.json()['images'][0]
        img_data = base64.b64decode(result)
        img = Image.open(io.BytesIO(img_data))
        img.save(weird_path)  # save original resolution first

        # Resize AFTER inpainting
        img.resize(resize_target, Image.LANCZOS).save(weird_path)

        padding = 50  # erhöht die Bounding Box Fläche künstlich für größere Objekte
        x, y, w, h = cv2.boundingRect(mask)
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(img_width - x, w + padding * 2)
        h = min(img_height - y, h + padding * 2)
        img_width, img_height = img_pil.size  # Originalgröße fürs Label

        # Normierung für 640x640
        resize_w, resize_h = resize_target

        x_center = (x + w / 2) / img_width
        y_center = (y + h / 2) / img_height
        norm_w = w / img_width
        norm_h = h / img_height
        x_center = (x + w / 2) / img_width
        y_center = (y + h / 2) / img_height
        norm_w = w / img_width
        norm_h = h / img_height

        with open(label_path, 'w') as f:
            f.write(f"0 {x_center} {y_center} {norm_w} {norm_h}")

    except Exception as e:
        print(f"[ERROR] Inpainting failed: {e}")
        fail_log.write(f"{clean_path} | Prompt: {full_prompt}\n")

images = [img for img in os.listdir(input_dir) if img.endswith(('.jpg', '.png'))]

train_imgs, temp_imgs = train_test_split(images, test_size=0.3, random_state=42)
val_imgs, test_imgs = train_test_split(temp_imgs, test_size=0.5, random_state=42)

splits = {
    'train': train_imgs,
    'val': val_imgs,
    'test': test_imgs,
}

for split_name, img_list in splits.items():
    for cls in ['clean', 'weird', 'labels']:
        os.makedirs(os.path.join(output_base, split_name, cls), exist_ok=True)

    selected_weird_imgs = random.sample(img_list, len(img_list))

    for img in img_list:
        clean_path = os.path.join(input_dir, img)
        mask_path = os.path.join(mask_dir, img.replace('.jpg', '.png'))

        clean_out = os.path.join(output_base, split_name, 'clean', img)
        shutil.copy(clean_path, clean_out)  # original image behalten

        if img in selected_weird_imgs:
            weird_out = os.path.join(output_base, split_name, 'weird', img)
            label_out = os.path.join(output_base, split_name, 'labels', img.replace('.jpg', '.txt').replace('.png', '.txt'))
            if not os.path.exists(weird_out) and not os.path.exists(label_out):
                generate_weird(clean_path, mask_path, weird_out, label_out, split_name)
            else:
                print(f"[SKIP] Already exists: {img}")

        # Nachträgliches Resizing
        Image.open(clean_out).resize(resize_target, Image.LANCZOS).save(clean_out)

fail_log.close()

print("\n✅ Split und Weird Image Generierung abgeschlossen!")
