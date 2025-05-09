import os

def create_missing_label_files(images_dir, labels_dir):
    """
    Find images without corresponding label files and create empty label files.
    
    Args:
        images_dir (str): Path to directory containing image files (.jpg)
        labels_dir (str): Path to directory containing label files (.txt)
    """
    # Get list of image files (without extension)
    image_files = [os.path.splitext(f)[0] for f in os.listdir(images_dir) 
                  if f.lower().endswith('.jpg') or f.lower().endswith('.jpeg')]
    
    # Get list of existing label files (without extension)
    label_files = [os.path.splitext(f)[0] for f in os.listdir(labels_dir) 
                  if f.lower().endswith('.txt')]
    
    # Find images without labels
    missing_labels = set(image_files) - set(label_files)
    
    # Create empty label files for missing ones
    for missing in missing_labels:
        label_path = os.path.join(labels_dir, f"{missing}.txt")
        with open(label_path, 'w') as f:
            pass  # Just create an empty file
        
        print(f"Created empty label file: {label_path}")
    
    print(f"\nProcess complete. Created {len(missing_labels)} empty label files.")

# Example usage
if __name__ == "__main__":
    images_directory = "/home/danielshaquille/Daniel/projects/datasets/chunk_6_shaquille/images"  # Replace with your images directory
    labels_directory = "/home/danielshaquille/Daniel/projects/datasets/chunk_6_shaquille/labels"  # Replace with your labels directory
    
    create_missing_label_files(images_directory, labels_directory)