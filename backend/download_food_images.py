import requests
import os
from urllib.parse import urlparse

print('=== Downloading Sample Food Images ===')

# Create images directory if it doesn't exist
images_dir = "static/images"
os.makedirs(images_dir, exist_ok=True)

# Sample food images from Unsplash (free to use)
food_images = {
    "butter_chicken.jpg": "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=400&h=300&fit=crop",
    "paneer_tikka.jpg": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400&h=300&fit=crop",
    "veg_biryani.jpg": "https://images.unsplash.com/photo-1586702902288-913544884c23?w=400&h=300&fit=crop",
    "chicken_biryani.jpg": "https://images.unsplash.com/photo-1589301768040-ba56ff76f6d5?w=400&h=300&fit=crop",
    "dal_makhani.jpg": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=400&h=300&fit=crop",
    "palak_paneer.jpg": "https://images.unsplash.com/photo-1569736658875-5a2a654b4b7f?w=400&h=300&fit=crop",
    "chicken_curry.jpg": "https://images.unsplash.com/photo-1587702757568-7896f9c9c9f6?w=400&h=300&fit=crop",
    "mix_veg.jpg": "https://images.unsplash.com/photo-1512058564366-18510be2c197?w=400&h=300&fit=crop",
    "noodles.jpg": "https://images.unsplash.com/photo-1563245370-fad24a0d53ea?w=400&h=300&fit=crop",
    "fried_rice.jpg": "https://images.unsplash.com/photo-1603133872878-68492bdc847a?w=400&h=300&fit=crop",
    "hot_coffee.jpg": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=300&fit=crop",
    "tea.jpg": "https://images.unsplash.com/photo-1564890369478-c89ca6d9cda9?w=400&h=300&fit=crop",
    "cold_coffee.jpg": "https://images.unsplash.com/photo-1512436996811-b0e6545ce3c7?w=400&h=300&fit=crop",
    "lime_soda.jpg": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=400&h=300&fit=crop",
    "mango_lassi.jpg": "https://images.unsplash.com/photo-1505252585461-04db1eb84625?w=400&h=300&fit=crop",
    "orange_juice.jpg": "https://images.unsplash.com/photo-1600271886742-f049be45f956?w=400&h=300&fit=crop",
    "samosa.jpg": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&h=300&fit=crop",
    "french_fries.jpg": "https://images.unsplash.com/photo-1576107612471-3170e8330eb0?w=400&h=300&fit=crop",
    "sandwich.jpg": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400&h=300&fit=crop",
    "pizza.jpg": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400&h=300&fit=crop",
    "burger.jpg": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop",
    "masala_dosa.jpg": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&h=300&fit=crop",
    "idli.jpg": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&h=300&fit=crop",
    "poha.jpg": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&h=300&fit=crop",
    "soup.jpg": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400&h=300&fit=crop",
    "tomato_soup.jpg": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400&h=300&fit=crop",
    "gulab_jamun.jpg": "https://images.unsplash.com/photo-1627834377411-8da5f4f09e8b?w=400&h=300&fit=crop",
    "ice_cream.jpg": "https://images.unsplash.com/photo-1488900128323-21503983a07e?w=400&h=300&fit=crop",
    "chocolate_cake.jpg": "https://images.unsplash.com/photo-1578985565032-9c11ca3d0d4b?w=400&h=300&fit=crop",
    "brownie.jpg": "https://images.unsplash.com/photo-1606313564200-e75d5e4a856e?w=400&h=300&fit=crop",
    "salad.jpg": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop",
    "caesar_salad.jpg": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop",
    "default_food.jpg": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop"
}

downloaded_count = 0

for filename, url in food_images.items():
    try:
        print(f"Downloading {filename}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        filepath = os.path.join(images_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        downloaded_count += 1
        print(f"✅ Downloaded: {filename}")
        
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        # Create a placeholder image if download fails
        try:
            # Create a simple colored placeholder
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np
            
            # Create a simple image with food name
            img = Image.new('RGB', (400, 300), color='#f0f0f0')
            draw = ImageDraw.Draw(img)
            
            # Add text
            food_name = filename.replace('_', ' ').replace('.jpg', '').title()
            try:
                # Try to use a default font
                font = ImageFont.load_default()
            except:
                font = None
            
            # Draw text centered
            text_bbox = draw.textbbox((0, 0), food_name, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (400 - text_width) // 2
            y = (300 - text_height) // 2
            
            draw.text((x, y), food_name, fill='#666666', font=font)
            
            filepath = os.path.join(images_dir, filename)
            img.save(filepath)
            downloaded_count += 1
            print(f"✅ Created placeholder: {filename}")
            
        except Exception as placeholder_error:
            print(f"❌ Failed to create placeholder for {filename}: {placeholder_error}")

print(f"\n🎉 Successfully downloaded/created {downloaded_count} food images!")
print(f"📁 Images stored in: {os.path.abspath(images_dir)}")
print(f"\n🌐 Access images at: http://localhost:8000/static/images/{filename}")
