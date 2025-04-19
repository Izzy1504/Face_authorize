#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw

def generate_images():
    # Get the base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(base_dir, "images")
    
    # Create images directory if it doesn't exist
    os.makedirs(images_dir, exist_ok=True)
    
    # Generate success image (tick)
    tick_path = os.path.join(images_dir, "tick.png")
    if not os.path.exists(tick_path):
        img = Image.new('RGB', (200, 200), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw a green tick (simple version)
        draw.line([(50, 100), (90, 140), (150, 70)], fill=(0, 200, 0), width=10)
        
        img.save(tick_path)
        print(f"Created {tick_path}")
    
    # Generate failure image (face)
    face_path = os.path.join(images_dir, "face.png")
    if not os.path.exists(face_path):
        img = Image.new('RGB', (200, 200), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw a red X
        draw.line([(50, 50), (150, 150)], fill=(200, 0, 0), width=10)
        draw.line([(50, 150), (150, 50)], fill=(200, 0, 0), width=10)
        
        img.save(face_path)
        print(f"Created {face_path}")

if __name__ == "__main__":
    generate_images()
    print("UI images generated successfully")
