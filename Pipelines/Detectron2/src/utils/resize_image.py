import os
from PIL import Image
from tqdm import tqdm

def resize_images_natural(input_folder, output_folder, target_size=(768, 768), quality=95):
    """
    Resize images naturally without padding, maintaining aspect ratio.
    The resized image will fit within target_size while preserving proportions.
    
    Args:
        input_folder (str): Path to source images
        output_folder (str): Path to save resized images
        target_size (tuple): Maximum (width, height) dimensions
        quality (int): JPEG quality (1-100)
    """
    os.makedirs(output_folder, exist_ok=True)
    
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
    images = [f for f in os.listdir(input_folder) 
             if f.lower().endswith(valid_extensions)]
    
    print(f"Resizing {len(images)} images to fit within {target_size}...")
    
    for img_file in tqdm(images):
        try:
            img_path = os.path.join(input_folder, img_file)
            img = Image.open(img_path)
            
            # Calculate new dimensions while maintaining aspect ratio
            width, height = img.size
            ratio = min(target_size[0]/width, target_size[1]/height)
            new_size = (int(width * ratio), int(height * ratio))
            
            # High-quality resizing
            resized = img.resize(new_size, Image.LANCZOS)
            
            # Save with original format and optimized quality
            output_path = os.path.join(output_folder, img_file)
            if img_file.lower().endswith(('.jpg', '.jpeg')):
                resized.save(output_path, 'JPEG', quality=quality, optimize=True)
            else:
                resized.save(output_path)
                
        except Exception as e:
            print(f"Error with {img_file}: {str(e)}")
    
    print(f"Successfully resized {len(images)} images in {output_folder}")

# Example usage
if __name__ == "__main__":
    input_folder = "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/coco_datasets/test"  # Change this
    output_folder = "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/resized_images"  # Change this
    target_size = (768, 768)  # Change to your desired size
    
    resize_images_natural(input_folder, output_folder, target_size=(768, 768))