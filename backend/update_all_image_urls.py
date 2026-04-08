import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.menu import MenuItem
from image_config import IMAGE_BASE_URL
import os

print('=== Update All Menu Items with Current Image URLs ===')

db = SessionLocal()

# Mapping of menu items to image files (same as before)
image_mapping = {
    'Butter Chicken': 'butter_chicken.jpg',
    'Paneer Tikka Masala': 'paneer_tikka.jpg',
    'Veg Biryani': 'veg_biryani.jpg',
    'Chicken Biryani': 'chicken_biryani.jpg',
    'Dal Makhani': 'dal_makhani.jpg',
    'Palak Paneer': 'palak_paneer.jpg',
    'Chicken Curry': 'chicken_curry.jpg',
    'Mix Veg': 'mix_veg.jpg',
    'Chicken Manchurian': 'noodles.jpg',
    'Veg Manchurian': 'noodles.jpg',
    'Noodles': 'noodles.jpg',
    'Fried Rice': 'fried_rice.jpg',
    'Steamed Rice': 'fried_rice.jpg',
    'Jeera Rice': 'fried_rice.jpg',
    'Curd Rice': 'fried_rice.jpg',
    'Hot Coffee': 'hot_coffee.jpg',
    'Hot Tea': 'tea.jpg',
    'Green Tea': 'tea.jpg',
    'Masala Chai': 'tea.jpg',
    'Cold Coffee': 'cold_coffee.jpg',
    'Fresh Lime Soda': 'lime_soda.jpg',
    'Mango Lassi': 'mango_lassi.jpg',
    'Sweet Lassi': 'mango_lassi.jpg',
    'Orange Juice': 'orange_juice.jpg',
    'Watermelon Juice': 'orange_juice.jpg',
    'Coca Cola': 'lime_soda.jpg',
    'Pepsi': 'lime_soda.jpg',
    'Sprite': 'lime_soda.jpg',
    'Mineral Water': 'lime_soda.jpg',
    'Samosa': 'samosa.jpg',
    'Pakora': 'samosa.jpg',
    'Vada Pav': 'samosa.jpg',
    'Kachori': 'samosa.jpg',
    'French Fries': 'french_fries.jpg',
    'Veg Sandwich': 'sandwich.jpg',
    'Chicken Sandwich': 'sandwich.jpg',
    'Cheese Pizza': 'pizza.jpg',
    'Veg Pizza': 'pizza.jpg',
    'Chicken Pizza': 'pizza.jpg',
    'Burger': 'burger.jpg',
    'Veg Burger': 'burger.jpg',
    'Masala Dosa': 'masala_dosa.jpg',
    'Plain Dosa': 'masala_dosa.jpg',
    'Idli Sambar': 'idli.jpg',
    'Poha': 'poha.jpg',
    'Upma': 'poha.jpg',
    'Egg Bhurji': 'mix_veg.jpg',
    'Boiled Eggs': 'mix_veg.jpg',
    'Bread Butter': 'sandwich.jpg',
    'Chicken Soup': 'soup.jpg',
    'Tomato Soup': 'tomato_soup.jpg',
    'Veg Manchow Soup': 'soup.jpg',
    'Sweet Corn Soup': 'soup.jpg',
    'Hot and Sour Soup': 'soup.jpg',
    'Gulab Jamun': 'gulab_jamun.jpg',
    'Rasgulla': 'gulab_jamun.jpg',
    'Ice Cream': 'ice_cream.jpg',
    'Chocolate Cake': 'chocolate_cake.jpg',
    'Brownie': 'brownie.jpg',
    'Kheer': 'gulab_jamun.jpg',
    'Halwa': 'gulab_jamun.jpg',
    'Green Salad': 'salad.jpg',
    'Caesar Salad': 'caesar_salad.jpg',
    'Greek Salad': 'caesar_salad.jpg',
    'Chicken Salad': 'caesar_salad.jpg'
}

try:
    # Get all menu items
    menu_items = db.query(MenuItem).all()
    
    updated_count = 0
    for item in menu_items:
        # Get the appropriate image file
        image_file = image_mapping.get(item.name, 'default_food.jpg')
        
        # Update the image_url with current base URL
        new_image_url = f"{IMAGE_BASE_URL}/{image_file}"
        
        if item.image_url != new_image_url:
            item.image_url = new_image_url
            updated_count += 1
            print(f"✅ Updated: {item.name}")
            print(f"   Old: {item.image_url}")
            print(f"   New: {new_image_url}")
            print()
    
    db.commit()
    
    print(f"🎉 Successfully updated {updated_count} menu items!")
    print(f"🌐 Current Base URL: {IMAGE_BASE_URL}")
    
    if updated_count == 0:
        print("✅ All menu items already have correct URLs!")
    
except Exception as e:
    print(f"❌ Error updating menu items: {e}")
    db.rollback()
finally:
    db.close()

print("\n📝 Usage Instructions:")
print("1. If you change server URL, update image_config.py")
print("2. Run this script to update all menu items automatically")
print("3. Or use flexible_image_urls.py to get current URLs manually")
