import os

print('=== Available Image URLs for Menu Management ===')

# Get the static images directory
images_dir = "static/images"

if not os.path.exists(images_dir):
    print("❌ Images directory not found!")
    print("Please run the download_food_images.py script first.")
else:
    print("📁 Copy these URLs for Menu Management:")
    print("=" * 60)
    
    # List all image files
    image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
    image_files.sort()
    
    base_url = "http://localhost:8000/static/images/"
    
    for i, filename in enumerate(image_files, 1):
        full_url = f"{base_url}{filename}"
        print(f"{i:2d}. {full_url}")
    
    print("=" * 60)
    print(f"📊 Total images available: {len(image_files)}")
    print(f"🌐 Base URL: {base_url}")
    print(f"📂 Local folder: {os.path.abspath(images_dir)}")
    
    print("\n📝 Instructions:")
    print("1. Copy any URL from above")
    print("2. Go to Admin Dashboard → Menu Management")
    print("3. Edit a menu item")
    print("4. Paste the URL in the 'Image URL' field")
    print("5. Save the item")
    
    print("\n🔄 For new images:")
    print("1. Place new image files in: static/images/")
    print("2. Refresh this list to see new URLs")
    print("3. Copy the new URL and use in menu management")
