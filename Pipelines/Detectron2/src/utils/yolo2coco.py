import os
import shutil
from sklearn.model_selection import train_test_split
from pylabel import importer
import json

def fix_annotation_ids(coco_file):
    """Ensure all annotation IDs are unique in the COCO JSON file"""
    with open(coco_file, 'r') as f:
        data = json.load(f)
    
    # Create unique IDs for annotations
    ann_id = 1
    for ann in data['annotations']:
        ann['id'] = ann_id
        ann_id += 1
    
    # Save fixed file
    with open(coco_file, 'w') as f:
        json.dump(data, f)


def split_and_convert_dataset():
    # Configuration
    input_path = "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/final_dataset"
    output_path = "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/coco_datasets"
    yoloclasses = ['weird_object']
    splits = ['train', 'val', 'test']
    img_ext = 'jpg'
    split_ratios = {'train': 0.8, 'val': 0.1, 'test': 0.1}

    # Create output directory structure
    os.makedirs(output_path, exist_ok=True)
    for split in splits:
        os.makedirs(os.path.join(output_path, split), exist_ok=True)

    # Collect all image files
    image_files = [f for f in os.listdir(input_path) if f.endswith(f'.{img_ext}')]
    image_files.sort()
    
    # Split dataset
    train_val, test_files = train_test_split(
        image_files, test_size=split_ratios['test'], random_state=42
    )
    train_files, val_files = train_test_split(
        train_val, test_size=split_ratios['val']/(1-split_ratios['test']), random_state=42
    )

    # Copy files to output directory structure
    for split in splits:
        split_dir = os.path.join(output_path, split)
        
        files = locals()[f'{split}_files']
        for file in files:
            # Copy image
            src_img = os.path.join(input_path, file)
            dst_img = os.path.join(split_dir, file)
            shutil.copy(src_img, dst_img)
            
            # Copy corresponding label
            txt_file = os.path.splitext(file)[0] + '.txt'
            src_txt = os.path.join(input_path, txt_file)
            dst_txt = os.path.join(split_dir, txt_file)
            if os.path.exists(src_txt):
                shutil.copy(src_txt, dst_txt)

    # Convert each split to COCO format
    for split in splits:
        split_dir = os.path.join(output_path, split)
        
        # Import YOLO dataset
        dataset = importer.ImportYoloV5(
            path=split_dir,
            path_to_images=split_dir,
            cat_names=yoloclasses,
            img_ext=img_ext,
            name=f"coco_{split}"
        )
        
        # Export to COCO format
        coco_output_path = os.path.join(output_path, f"{split}_annotations.json")
        dataset.export.ExportToCoco(coco_output_path)
        
        # Fix annotation IDs
        fix_annotation_ids(coco_output_path)
        print(f"Created and fixed COCO annotations for {split} set at: {coco_output_path}")

        # Delete all .txt files in the split directory
        for file in os.listdir(split_dir):
            if file.endswith('.txt'):
                os.remove(os.path.join(split_dir, file))

if __name__ == "__main__":
    split_and_convert_dataset()