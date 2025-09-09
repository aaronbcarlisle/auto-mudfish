#!/usr/bin/env python3
"""
Create a proper icon for Auto Mudfish VPN.

This script creates an icon that combines the Mudfish logo with an "Auto" indicator.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

def create_mudfish_icon():
    """Create the Auto Mudfish icon."""
    print("Creating Auto Mudfish icon...")
    
    # Icon sizes to generate
    sizes = [16, 32, 48, 64, 128, 256]
    
    # Create a simple Mudfish-inspired icon
    # We'll create a fish-like shape with an "A" overlay
    
    for size in sizes:
        # Create base image with transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Calculate dimensions based on size
        margin = size // 8
        fish_width = size - 2 * margin
        fish_height = size - 2 * margin
        
        # Create fish body (oval shape)
        fish_x = margin
        fish_y = margin
        fish_rect = [fish_x, fish_y, fish_x + fish_width, fish_y + fish_height]
        
        # Fish body color (Mudfish blue-ish)
        fish_color = (0, 100, 200, 255)  # Blue with alpha
        draw.ellipse(fish_rect, fill=fish_color, outline=(0, 80, 160, 255))
        
        # Add fish tail
        tail_width = fish_width // 4
        tail_height = fish_height // 2
        tail_x = fish_x + fish_width - tail_width
        tail_y = fish_y + (fish_height - tail_height) // 2
        
        # Tail points
        tail_points = [
            (tail_x, tail_y),
            (fish_x + fish_width, tail_y + tail_height // 2),
            (tail_x, tail_y + tail_height)
        ]
        draw.polygon(tail_points, fill=fish_color)
        
        # Add fish eye
        eye_size = size // 8
        eye_x = fish_x + fish_width // 3
        eye_y = fish_y + fish_height // 3
        eye_rect = [eye_x, eye_y, eye_x + eye_size, eye_y + eye_size]
        draw.ellipse(eye_rect, fill=(255, 255, 255, 255))
        
        # Add pupil
        pupil_size = eye_size // 2
        pupil_x = eye_x + eye_size // 4
        pupil_y = eye_y + eye_size // 4
        pupil_rect = [pupil_x, pupil_y, pupil_x + pupil_size, pupil_y + pupil_size]
        draw.ellipse(pupil_rect, fill=(0, 0, 0, 255))
        
        # Add "A" overlay for "Auto"
        try:
            # Try to use a system font
            font_size = size // 3
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
        
        # Calculate text position
        text = "A"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = fish_x + fish_width - text_width - size // 8
        text_y = fish_y + (fish_height - text_height) // 2
        
        # Draw "A" with white color and black outline
        draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))
        
        # Add a small circle background for the "A"
        circle_size = text_width + size // 16
        circle_x = text_x - size // 32
        circle_y = text_y - size // 32
        circle_rect = [circle_x, circle_y, circle_x + circle_size, circle_y + circle_size]
        draw.ellipse(circle_rect, fill=(255, 0, 0, 200))  # Red circle with transparency
        
        # Redraw "A" on top of circle
        draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))
        
        # Save individual size
        icon_path = f'../assets/icon_{size}x{size}.png'
        os.makedirs(os.path.dirname(icon_path), exist_ok=True)
        img.save(icon_path, 'PNG')
        print(f"Created {icon_path}")
    
    # Create ICO file with multiple sizes
    ico_path = '../assets/icon.ico'
    os.makedirs(os.path.dirname(ico_path), exist_ok=True)
    
    # Load all sizes and save as ICO
    images = []
    for size in sizes:
        img_path = f'../assets/icon_{size}x{size}.png'
        if os.path.exists(img_path):
            img = Image.open(img_path)
            images.append(img)
    
    if images:
        images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in images])
        print(f"Created {ico_path}")
        
        # Clean up individual PNG files
        for size in sizes:
            png_path = f'../assets/icon_{size}x{size}.png'
            if os.path.exists(png_path):
                os.remove(png_path)
        
        print("Icon creation completed!")
        return True
    else:
        print("Failed to create icon images!")
        return False

def create_simple_icon():
    """Create a simple fallback icon if the main creation fails."""
    print("Creating simple fallback icon...")
    
    # Create a simple 256x256 icon
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple fish shape
    fish_rect = [50, 50, 206, 206]
    draw.ellipse(fish_rect, fill=(0, 100, 200, 255), outline=(0, 80, 160, 255))
    
    # Add "A" in the corner
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    draw.text((180, 180), "A", font=font, fill=(255, 255, 255, 255))
    
    # Save as ICO
    ico_path = '../assets/icon.ico'
    os.makedirs(os.path.dirname(ico_path), exist_ok=True)
    img.save(ico_path, format='ICO', sizes=[(256, 256)])
    print(f"Created simple icon: {ico_path}")
    return True

if __name__ == "__main__":
    try:
        success = create_mudfish_icon()
        if not success:
            print("Falling back to simple icon...")
            create_simple_icon()
    except Exception as e:
        print(f"Error creating icon: {e}")
        print("Creating simple fallback icon...")
        create_simple_icon()
