import os

def delete_unpaired_files(folder_path):
    """
    Delete unpaired .jpg/.txt files in a folder (YOLO format cleanup).
    Keeps only files that have both image and annotation pairs.
    """
    # Get all files in the directory
    all_files = os.listdir(folder_path)
    
    # Separate into images and annotations
    jpg_files = {f[:-4] for f in all_files if f.lower().endswith('.jpg')}
    txt_files = {f[:-4] for f in all_files if f.lower().endswith('.txt')}
    
    # Find unpaired files
    unpaired_jpg = jpg_files - txt_files
    unpaired_txt = txt_files - jpg_files
    
    # Delete unpaired files
    deleted_count = 0
    for basename in unpaired_jpg:
        file_path = os.path.join(folder_path, basename + '.jpg')
        os.remove(file_path)
        print(f"Deleted unpaired image: {file_path}")
        deleted_count += 1
    
    for basename in unpaired_txt:
        file_path = os.path.join(folder_path, basename + '.txt')
        os.remove(file_path)
        print(f"Deleted unpaired annotation: {file_path}")
        deleted_count += 1
    
    print(f"\nDeleted {deleted_count} unpaired files")
    print(f"Remaining: {len(jpg_files & txt_files)} valid pairs")


delete_unpaired_files(folder_path="/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/resized_images")
