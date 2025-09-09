#!/usr/bin/env python3
"""
Create Auto Mudfish icon by overlaying automation symbol on Mudfish icon.
"""

from PIL import Image, ImageDraw, ImageFont
import os
import sys

def create_auto_mudfish_icon():
    """Create the Auto Mudfish icon with automation overlay."""
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    assets_dir = os.path.join(project_root, "assets")
    
    # Create assets directory if it doesn't exist
    os.makedirs(assets_dir, exist_ok=True)
    
    # Icon sizes to generate
    sizes = [16, 32, 48, 64, 128, 256]
    
    for size in sizes:
        print(f"Creating {size}x{size} icon...")
        
        # Create base icon (Mudfish fish shape)
        icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        # Draw Mudfish icon (simplified fish shape)
        # Fish body (yellow/gold)
        fish_color = (255, 215, 0)  # Gold
        outline_color = (0, 0, 0)   # Black
        
        # Calculate fish dimensions based on icon size (reduced padding)
        fish_width = int(size * 0.85)  # Increased from 0.7
        fish_height = int(size * 0.6)  # Increased from 0.5
        fish_x = int(size * 0.05)      # Reduced from 0.15
        fish_y = int(size * 0.2)       # Reduced from 0.25
        
        # Draw fish body (triangle/oval shape)
        fish_points = [
            (fish_x, fish_y + fish_height // 2),  # Left point (tail)
            (fish_x + fish_width, fish_y),        # Top right
            (fish_x + fish_width, fish_y + fish_height),  # Bottom right
        ]
        draw.polygon(fish_points, fill=fish_color, outline=outline_color, width=2)
        
        # Draw fish eye
        eye_size = max(2, size // 16)
        eye_x = fish_x + int(fish_width * 0.3)
        eye_y = fish_y + int(fish_height * 0.3)
        draw.ellipse([eye_x - eye_size, eye_y - eye_size, 
                     eye_x + eye_size, eye_y + eye_size], 
                    fill=(255, 255, 255), outline=outline_color, width=1)
        
        # Draw pupil
        pupil_size = max(1, size // 32)
        draw.ellipse([eye_x - pupil_size, eye_y - pupil_size, 
                     eye_x + pupil_size, eye_y + pupil_size], 
                    fill=outline_color)
        
        # Draw mouth
        mouth_y = fish_y + int(fish_height * 0.7)
        mouth_x = fish_x + int(fish_width * 0.8)
        draw.line([mouth_x, mouth_y, mouth_x + size // 16, mouth_y], 
                 fill=outline_color, width=1)
        
        # Add automation overlay (gear symbol) - larger and better positioned
        overlay_size = int(size * 0.35)  # Increased from 0.3
        overlay_x = fish_x + int(fish_width * 0.55)  # Adjusted position
        overlay_y = fish_y + int(fish_height * 0.55)  # Adjusted position
        
        # Draw gear (simplified)
        gear_color = (0, 100, 200)  # Blue
        gear_outline = (255, 255, 255)  # White outline
        
        # Main gear circle
        gear_radius = overlay_size // 2
        draw.ellipse([overlay_x - gear_radius, overlay_y - gear_radius,
                     overlay_x + gear_radius, overlay_y + gear_radius],
                    fill=gear_color, outline=gear_outline, width=1)
        
        # Gear teeth (simplified - just small rectangles)
        tooth_size = max(1, size // 32)
        for angle in range(0, 360, 45):  # 8 teeth
            import math
            rad = math.radians(angle)
            tooth_x = overlay_x + int((gear_radius - tooth_size) * math.cos(rad))
            tooth_y = overlay_y + int((gear_radius - tooth_size) * math.sin(rad))
            draw.rectangle([tooth_x - tooth_size//2, tooth_y - tooth_size//2,
                           tooth_x + tooth_size//2, tooth_y + tooth_size//2],
                          fill=gear_color, outline=gear_outline)
        
        # Add "AUTO" text (larger and more prominent)
        try:
            # Try to use a system font with larger size
            font_size = max(6, size // 6)  # Increased from size // 8
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Draw "AUTO" text
        text = "AUTO"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = overlay_x - text_width // 2
        text_y = overlay_y - text_height // 2
        
        # Draw text with white outline
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    draw.text((text_x + dx, text_y + dy), text, 
                            fill=(255, 255, 255), font=font)
        
        # Draw main text
        draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font)
        
        # Save the icon
        icon_path = os.path.join(assets_dir, f"auto_mudfish_{size}x{size}.png")
        icon.save(icon_path, "PNG")
        print(f"Saved: {icon_path}")
    
    # Create ICO file for Windows
    print("Creating ICO file...")
    ico_images = []
    for size in [16, 32, 48, 64, 128, 256]:
        icon_path = os.path.join(assets_dir, f"auto_mudfish_{size}x{size}.png")
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            ico_images.append(img)
    
    if ico_images:
        ico_path = os.path.join(assets_dir, "auto_mudfish.ico")
        ico_images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in ico_images])
        print(f"Saved: {ico_path}")
    
    print("Icon creation completed!")

if __name__ == "__main__":
    create_auto_mudfish_icon()
