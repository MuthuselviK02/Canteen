import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.menu import MenuItem

print('=== Updating Menu Items with Proper Image URLs ===')

db = SessionLocal()

# Mapping of menu items to image files
image_mapping = {
    # Main Course - Indian
    'Butter Chicken': 'butter_chicken.jpg',
    'Paneer Tikka Masala': 'paneer_tikka.jpg',
    'Veg Biryani': 'veg_biryani.jpg',
    'Chicken Biryani': 'chicken_biryani.jpg',
    'Dal Makhani': 'dal_makhani.jpg',
    'Palak Paneer': 'palak_paneer.jpg',
    'Chicken Curry': 'chicken_curry.jpg',
    'Mix Veg': 'mix_veg.jpg',
    
    # Main Course - Chinese
    'Chicken Manchurian': 'noodles.jpg',
    'Veg Manchurian': 'noodles.jpg',
    'Noodles': 'noodles.jpg',
    'Fried Rice': 'fried_rice.jpg',
    
    # Rice Items
    'Steamed Rice': 'fried_rice.jpg',
    'Jeera Rice': 'fried_rice.jpg',
    'Curd Rice': 'fried_rice.jpg',
    
    # Beverages - Hot
    'Hot Coffee': 'hot_coffee.jpg',
    'Hot Tea': 'tea.jpg',
    'Green Tea': 'tea.jpg',
    'Masala Chai': 'tea.jpg',
    
    # Beverages - Cold
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
    
    # Snacks - Indian
    'Samosa': 'samosa.jpg',
    'Pakora': 'samosa.jpg',
    'Vada Pav': 'samosa.jpg',
    'Kachori': 'samosa.jpg',
    
    # Snacks - Continental
    'French Fries': 'french_fries.jpg',
    'Veg Sandwich': 'sandwich.jpg',
    'Chicken Sandwich': 'sandwich.jpg',
    'Cheese Pizza': 'pizza.jpg',
    'Veg Pizza': 'pizza.jpg',
    'Chicken Pizza': 'pizza.jpg',
    'Burger': 'burger.jpg',
    'Veg Burger': 'burger.jpg',
    
    # Breakfast
    'Masala Dosa': 'masala_dosa.jpg',
    'Plain Dosa': 'masala_dosa.jpg',
    'Idli Sambar': 'idli.jpg',
    'Poha': 'poha.jpg',
    'Upma': 'poha.jpg',
    'Egg Bhurji': 'mix_veg.jpg',
    'Boiled Eggs': 'mix_veg.jpg',
    'Bread Butter': 'sandwich.jpg',
    
    # Soup
    'Chicken Soup': 'soup.jpg',
    'Tomato Soup': 'tomato_soup.jpg',
    'Veg Manchow Soup': 'soup.jpg',
    'Sweet Corn Soup': 'soup.jpg',
    'Hot and Sour Soup': 'soup.jpg',
    
    # Dessert
    'Gulab Jamun': 'gulab_jamun.jpg',
    'Rasgulla': 'gulab_jamun.jpg',
    'Ice Cream': 'ice_cream.jpg',
    'Chocolate Cake': 'chocolate_cake.jpg',
    'Brownie': 'brownie.jpg',
    'Kheer': 'gulab_jamun.jpg',
    'Halwa': 'gulab_jamun.jpg',
    
    # Salad
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
        
        # Update the image_url to point to our static files
        new_image_url = f"/static/images/{image_file}"
        
        if item.image_url != new_image_url:
            item.image_url = new_image_url
            updated_count += 1
            print(f"✅ Updated: {item.name} -> {new_image_url}")
    
    db.commit()
    
    print(f"\n🎉 Successfully updated {updated_count} menu items with proper image URLs!")
    
    # Test a few items
    print("\n🧪 Sample updated items:")
    sample_items = db.query(MenuItem).limit(5).all()
    for item in sample_items:
        print(f"   - {item.name}: {item.image_url}")
    
    print(f"\n🌐 Images will be served at: http://localhost:8000/static/images/[filename]")
    
except Exception as e:
    print(f"❌ Error updating menu items: {e}")
    db.rollback()
finally:
    db.close()
