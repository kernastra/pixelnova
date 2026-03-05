#!/usr/bin/env python3
"""
Example script demonstrating the Photo Upscaler CLI
"""

from pathlib import Path
from PIL import Image

def create_sample_images():
    """Create sample images for testing"""
    input_folder = Path('input')
    input_folder.mkdir(exist_ok=True)
    
    # Create 3 sample images
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Red, Green, Blue
    
    for i, color in enumerate(colors):
        # Create a simple colored image
        img = Image.new('RGB', (100, 100), color)
        
        # Add some simple pattern
        for x in range(0, 100, 10):
            for y in range(0, 100, 10):
                if (x + y) % 20 == 0:
                    img.putpixel((x, y), (255, 255, 255))
        
        # Save the image
        img.save(input_folder / f'sample_{i+1}.png')
        print(f"Created sample_{i+1}.png")

def main():
    print("🖼️  Photo Upscaler CLI - Example")
    print("=" * 40)
    
    # Create sample images
    create_sample_images()
    
    print("\nSample images created in 'input' folder!")
    print("\nNow you can test the upscaler:")
    print("1. Basic upscaling: python upscaler.py")
    print("2. With custom naming: python upscaler.py --prompt-name")
    print("3. 4x upscaling: python upscaler.py --scale 4.0")

if __name__ == '__main__':
    main()
