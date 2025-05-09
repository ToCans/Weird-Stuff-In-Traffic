import os
import shutil
import random
from sklearn.model_selection import train_test_split

def split_yolo_dataset(images_dir, labels_dir, output_dir, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1, random_seed=42):
    """
    Split YOLO dataset into train, validation, and test sets.
    
    Args:
        images_dir (str): Path to directory containing image files
        labels_dir (str): Path to directory containing label files
        output_dir (str): Path to output directory where split datasets will be saved
        train_ratio (float): Proportion of data for training set
        val_ratio (float): Proportion of data for validation set
        test_ratio (float): Proportion of data for test set
        random_seed (int): Random seed for reproducibility
    """
    # Validate ratios
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 0.0001, "Ratios must sum to 1"
    
    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    train_img_dir = os.path.join(output_dir, 'train', 'images')
    train_label_dir = os.path.join(output_dir, 'train', 'labels')
    val_img_dir = os.path.join(output_dir, 'val', 'images')
    val_label_dir = os.path.join(output_dir, 'val', 'labels')
    test_img_dir = os.path.join(output_dir, 'test', 'images')
    test_label_dir = os.path.join(output_dir, 'test', 'labels')
    
    for dir_path in [train_img_dir, train_label_dir, val_img_dir, val_label_dir, test_img_dir, test_label_dir]:
        os.makedirs(dir_path, exist_ok=True)
    
    # Get list of image files (without extension)
    image_files = [f for f in os.listdir(images_dir) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    base_names = [os.path.splitext(f)[0] for f in image_files]
    
    # Verify that all images have corresponding label files
    valid_pairs = []
    for base in base_names:
        label_file = f"{base}.txt"
        if os.path.exists(os.path.join(labels_dir, label_file)):
            valid_pairs.append(base)
        else:
            print(f"Warning: No label file found for {base}.jpg - skipping")
    
    # Split the dataset
    random.seed(random_seed)
    random.shuffle(valid_pairs)
    
    # First split into train and temp (val+test)
    train, temp = train_test_split(valid_pairs, train_size=train_ratio, random_state=random_seed)
    
    # Then split temp into val and test
    val_test_ratio = val_ratio / (val_ratio + test_ratio)
    val, test = train_test_split(temp, train_size=val_test_ratio, random_state=random_seed)
    
    # Function to copy files
    def copy_files(names, img_source, label_source, img_dest, label_dest):
        for name in names:
            # Find the original image file (could be .jpg, .jpeg, or .png)
            img_ext = None
            for ext in ['.jpg', '.jpeg', '.png']:
                if os.path.exists(os.path.join(img_source, f"{name}{ext}")):
                    img_ext = ext
                    break
            
            if img_ext:
                # Copy image
                shutil.copy2(
                    os.path.join(img_source, f"{name}{img_ext}"),
                    os.path.join(img_dest, f"{name}{img_ext}")
                )
                # Copy label
                shutil.copy2(
                    os.path.join(label_source, f"{name}.txt"),
                    os.path.join(label_dest, f"{name}.txt")
                )
    
    # Copy files to their respective directories
    copy_files(train, images_dir, labels_dir, train_img_dir, train_label_dir)
    copy_files(val, images_dir, labels_dir, val_img_dir, val_label_dir)
    copy_files(test, images_dir, labels_dir, test_img_dir, test_label_dir)
    
    print("\nDataset split completed successfully!")
    print(f"Total files: {len(valid_pairs)}")
    print(f"Train set: {len(train)} files ({len(train)/len(valid_pairs):.1%})")
    print(f"Validation set: {len(val)} files ({len(val)/len(valid_pairs):.1%})")
    print(f"Test set: {len(test)} files ({len(test)/len(valid_pairs):.1%})")

# Example usage
if __name__ == "__main__":
    # Set your paths here
    images_directory = "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_coco/images"
    labels_directory = "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_coco/labels"
    output_directory = "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_coco/splitted_data"
    
    # Set your desired ratios (must sum to 1)
    train_ratio = 0.7  # 70% for training
    val_ratio = 0.2    # 20% for validation
    test_ratio = 0.1   # 10% for testing
    
    split_yolo_dataset(
        images_dir=images_directory,
        labels_dir=labels_directory,
        output_dir=output_directory,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio
    )