import os
from image_config import IMAGE_BASE_URL

print('=== Flexible Image URLs for Menu Management ===')

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
    
    print(f"🌐 Current Base URL: {IMAGE_BASE_URL}")
    print("=" * 60)
    
    for i, filename in enumerate(image_files, 1):
        full_url = f"{IMAGE_BASE_URL}/{filename}"
        local_path = os.path.abspath(os.path.join(images_dir, filename))
        print(f"{i:2d}. {full_url}")
        print(f"    📁 Local: {local_path}")
        print()
    
    print("=" * 60)
    print(f"📊 Total images available: {len(image_files)}")
    print(f"🌐 Base URL: {IMAGE_BASE_URL}")
    print(f"📂 Local folder: {os.path.abspath(images_dir)}")
    
    print("\n📝 Instructions:")
    print("1. Copy any URL from above for web use")
    print("2. Local paths shown for reference only")
    print("3. If server URL changes, update image_config.py")
    print("4. Run this script again to get updated URLs")
    
    print("\n🔄 For new images:")
    print("1. Place new image files in: static/images/")
    print("2. Refresh this list to see new URLs")
    print("3. Copy the new URL and use in menu management")
    
    print("\n⚙️  To change base URL:")
    print("1. Edit image_config.py")
    print("2. Update BASE_URL variable")
    print("3. Run this script again")
