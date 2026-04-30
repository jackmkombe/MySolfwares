from PIL import Image
import os

png_path = r'C:\Users\etoun\.gemini\antigravity\brain\8e2ab42c-6d0f-4cae-95f6-fa8fffb371b7\medianexus_ultra_icon_source_1767310849628.png'
ico_path = r'c:\Users\etoun\Documents\Nouveau dossier\MediaNexus_Ultra\app_icon.ico'

os.makedirs(os.path.dirname(ico_path), exist_ok=True)

if os.path.exists(png_path):
    img = Image.open(png_path)
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, sizes=icon_sizes)
    print(f"Icon MediaNexus Ultra saved successfully at {ico_path}")
else:
    print(f"Error: PNG not found at {png_path}")
