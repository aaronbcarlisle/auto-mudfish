#!/usr/bin/env python3
"""
Create a simple icon for the Auto Mudfish application using PIL.
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    def create_icon():
        """Create a simple icon for the application."""
        # Create a 256x256 image with a blue background
        size = (256, 256)
        img = Image.new('RGBA', size, (33, 150, 243, 255))  # Blue background
        draw = ImageDraw.Draw(img)
        
        # Draw a white circle in the center
        circle_center = (128, 128)
        circle_radius = 80
        draw.ellipse(
            [circle_center[0] - circle_radius, circle_center[1] - circle_radius,
             circle_center[0] + circle_radius, circle_center[1] + circle_radius],
            fill=(255, 255, 255, 255)
        )
        
        # Draw "M" for Mudfish in the center
        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", 120)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 120)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
        
        # Calculate text position to center it
        text = "M"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (size[0] - text_width) // 2
        text_y = (size[1] - text_height) // 2 - 10  # Slight adjustment
        
        draw.text((text_x, text_y), text, fill=(33, 150, 243, 255), font=font)
        
        # Save as ICO file
        img.save('icon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        print("Icon created: icon.ico")
        
    if __name__ == "__main__":
        create_icon()
        
except ImportError:
    print("PIL (Pillow) not found. Creating a simple placeholder icon...")
    
    # Create a simple text file as placeholder
    with open('icon.ico', 'w') as f:
        f.write("Placeholder icon file")
    
    print("Placeholder icon created: icon.ico")
    print("To create a proper icon, install Pillow: pip install Pillow")
