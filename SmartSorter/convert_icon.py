from PIL import Image
import os

png_path = r'C:\Users\etoun\.gemini\antigravity\brain\8e2ab42c-6d0f-4cae-95f6-fa8fffb371b7\smart_sorter_icon_1767308583737.png'
ico_path = r'c:\Users\etoun\Documents\Nouveau dossier\app_icon.ico'

if os.path.exists(png_path):
    img = Image.open(png_path)
    # Resize and save as ICO with multiple sizes for better compatibility
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, sizes=icon_sizes)
    print(f"Icon saved successfully at {ico_path}")
else:
    print(f"Error: PNG not found at {png_path}")
