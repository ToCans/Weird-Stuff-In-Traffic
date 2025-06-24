import os
from PIL import Image

def convert_png_to_jpg(folder_path, delete_original=False):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.png'):
            png_path = os.path.join(folder_path, filename)
            jpg_filename = os.path.splitext(filename)[0] + '.jpg'
            jpg_path = os.path.join(folder_path, jpg_filename)

            try:
                with Image.open(png_path) as img:
                    rgb_img = img.convert('RGB')  # Remove alpha if present
                    rgb_img.save(jpg_path, 'JPEG', quality=95)
                    print(f"✅ Converted: {filename} -> {jpg_filename}")

                if delete_original:
                    os.remove(png_path)
                    print(f"🗑️ Deleted original: {filename}")
            except Exception as e:
                print(f"❌ Failed to convert {filename}: {e}")

if __name__ == "__main__":
    folder = "/home/danielshaquille/Daniel/projects/datasets/weird_stuff_in_traffic/png2jpg"  # Replace with your folder path
    convert_png_to_jpg(folder, delete_original=True)  # Set to False if you want to keep PNGs
