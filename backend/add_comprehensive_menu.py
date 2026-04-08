import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.menu import MenuItem
from datetime import datetime

print('=== Adding Comprehensive Menu Items ===')

db = SessionLocal()

# Comprehensive menu items across all categories
menu_items = [
    # MAIN COURSE - Indian
    {
        'name': 'Butter Chicken',
        'description': 'Tender chicken cooked in rich, creamy tomato-based curry with butter and aromatic spices',
        'category': 'Main Course',
        'price': 280.00,
        'calories': 450,
        'is_vegetarian': False,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Paneer Tikka Masala',
        'description': 'Cottage cheese cubes marinated in spices and grilled, then simmered in creamy tomato gravy',
        'category': 'Main Course',
        'price': 220.00,
        'calories': 380,
        'is_vegetarian': True,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Veg Biryani',
        'description': 'Fragrant basmati rice cooked with mixed vegetables, aromatic spices, and herbs',
        'category': 'Main Course',
        'price': 180.00,
        'calories': 320,
        'is_vegetarian': True,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Chicken Biryani',
        'description': 'Aromatic basmati rice with tender chicken pieces, spices, and herbs',
        'category': 'Main Course',
        'price': 250.00,
        'calories': 420,
        'is_vegetarian': False,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Dal Makhani',
        'description': 'Creamy black lentils cooked with butter and aromatic spices',
        'category': 'Main Course',
        'price': 160.00,
        'calories': 280,
        'is_vegetarian': True,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Palak Paneer',
        'description': 'Cottage cheese cubes in creamy spinach gravy with aromatic spices',
        'category': 'Main Course',
        'price': 200.00,
        'calories': 320,
        'is_vegetarian': True,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Chicken Curry',
        'description': 'Tender chicken pieces cooked in aromatic Indian spices with onion-tomato base',
        'category': 'Main Course',
        'price': 240.00,
        'calories': 380,
        'is_vegetarian': False,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Mix Veg',
        'description': 'Mixed vegetables cooked in Indian spices with gravy',
        'category': 'Main Course',
        'price': 140.00,
        'calories': 220,
        'is_vegetarian': True,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    
    # MAIN COURSE - Chinese
    {
        'name': 'Chicken Manchurian',
        'description': 'Crispy chicken balls in spicy Manchurian gravy',
        'category': 'Main Course',
        'price': 220.00,
        'calories': 340,
        'is_vegetarian': False,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Veg Manchurian',
        'description': 'Crispy vegetable balls in spicy Manchurian gravy',
        'category': 'Main Course',
        'price': 180.00,
        'calories': 280,
        'is_vegetarian': True,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Noodles',
        'description': 'Stir-fried noodles with vegetables and soy sauce',
        'category': 'Main Course',
        'price': 120.00,
        'calories': 280,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Fried Rice',
        'description': 'Stir-fried rice with vegetables, eggs, and soy sauce',
        'category': 'Main Course',
        'price': 140.00,
        'calories': 320,
        'is_vegetarian': False,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    
    # BEVERAGES - Hot
    {
        'name': 'Hot Coffee',
        'description': 'Freshly brewed coffee with milk and sugar',
        'category': 'Beverage',
        'price': 40.00,
        'calories': 80,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Hot Tea',
        'description': 'Freshly brewed tea with milk and sugar',
        'category': 'Beverage',
        'price': 25.00,
        'calories': 40,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Green Tea',
        'description': 'Refreshing green tea without milk',
        'category': 'Beverage',
        'price': 30.00,
        'calories': 20,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Masala Chai',
        'description': 'Spiced Indian tea with aromatic spices',
        'category': 'Beverage',
        'price': 35.00,
        'calories': 60,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    
    # BEVERAGES - Cold
    {
        'name': 'Cold Coffee',
        'description': 'Chilled coffee with milk, ice, and chocolate syrup',
        'category': 'Beverage',
        'price': 60.00,
        'calories': 150,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Fresh Lime Soda',
        'description': 'Refreshing drink with fresh lime juice, soda, and mint',
        'category': 'Beverage',
        'price': 40.00,
        'calories': 60,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Mango Lassi',
        'description': 'Creamy yogurt drink with sweet mango pulp and cardamom',
        'category': 'Beverage',
        'price': 50.00,
        'calories': 120,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Sweet Lassi',
        'description': 'Creamy yogurt drink with sugar and cardamom',
        'category': 'Beverage',
        'price': 40.00,
        'calories': 100,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Orange Juice',
        'description': 'Fresh orange juice without added sugar',
        'category': 'Beverage',
        'price': 50.00,
        'calories': 80,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Watermelon Juice',
        'description': 'Fresh watermelon juice with mint',
        'category': 'Beverage',
        'price': 45.00,
        'calories': 60,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Coca Cola',
        'description': 'Classic cola drink',
        'category': 'Beverage',
        'price': 30.00,
        'calories': 140,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Pepsi',
        'description': 'Refreshing cola drink',
        'category': 'Beverage',
        'price': 30.00,
        'calories': 140,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Sprite',
        'description': 'Lemon-lime flavored soft drink',
        'category': 'Beverage',
        'price': 30.00,
        'calories': 140,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Mineral Water',
        'description': 'Pure mineral water',
        'category': 'Beverage',
        'price': 20.00,
        'calories': 0,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    
    # SNACKS - Indian
    {
        'name': 'Samosa',
        'description': 'Crispy pastry filled with spiced potatoes and peas, served with chutney',
        'category': 'Snacks',
        'price': 25.00,
        'calories': 150,
        'is_vegetarian': True,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Pakora',
        'description': 'Crispy fritters made with gram flour and vegetables',
        'category': 'Snacks',
        'price': 60.00,
        'calories': 200,
        'is_vegetarian': True,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Vada Pav',
        'description': 'Spicy potato fritter in a bun with chutney',
        'category': 'Snacks',
        'price': 35.00,
        'calories': 250,
        'is_vegetarian': True,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Kachori',
        'description': 'Crispy pastry filled with spiced lentils',
        'category': 'Snacks',
        'price': 30.00,
        'calories': 180,
        'is_vegetarian': True,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    
    # SNACKS - Continental
    {
        'name': 'French Fries',
        'description': 'Crispy golden potato fries seasoned with salt and herbs',
        'category': 'Snacks',
        'price': 50.00,
        'calories': 220,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Veg Sandwich',
        'description': 'Fresh vegetables with cheese and chutney grilled between bread slices',
        'category': 'Snacks',
        'price': 60.00,
        'calories': 200,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Chicken Sandwich',
        'description': 'Grilled chicken with lettuce, tomato, and mayo in toasted bread',
        'category': 'Snacks',
        'price': 80.00,
        'calories': 250,
        'is_vegetarian': False,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Cheese Pizza',
        'description': 'Classic pizza with mozzarella cheese and tomato sauce',
        'category': 'Snacks',
        'price': 120.00,
        'calories': 280,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Veg Pizza',
        'description': 'Pizza loaded with fresh vegetables and cheese',
        'category': 'Snacks',
        'price': 150.00,
        'calories': 320,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Chicken Pizza',
        'description': 'Pizza with grilled chicken and cheese',
        'category': 'Snacks',
        'price': 180.00,
        'calories': 380,
        'is_vegetarian': False,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Burger',
        'description': 'Classic beef burger with lettuce, tomato, and cheese',
        'category': 'Snacks',
        'price': 100.00,
        'calories': 350,
        'is_vegetarian': False,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Veg Burger',
        'description': 'Vegetarian patty with lettuce, tomato, and cheese',
        'category': 'Snacks',
        'price': 80.00,
        'calories': 280,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    
    # BREAKFAST
    {
        'name': 'Masala Dosa',
        'description': 'Crispy rice crepe filled with spiced potato mixture, served with sambar and chutney',
        'category': 'Breakfast',
        'price': 120.00,
        'calories': 280,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Plain Dosa',
        'description': 'Crispy rice crepe served with sambar and chutney',
        'category': 'Breakfast',
        'price': 80.00,
        'calories': 200,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Idli Sambar',
        'description': 'Steamed rice cakes served with flavorful lentil soup and coconut chutney',
        'category': 'Breakfast',
        'price': 80.00,
        'calories': 180,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Poha',
        'description': 'Flattened rice cooked with onions, peanuts, and spices',
        'category': 'Breakfast',
        'price': 60.00,
        'calories': 160,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Upma',
        'description': 'Semolina porridge cooked with vegetables and spices',
        'category': 'Breakfast',
        'price': 50.00,
        'calories': 140,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Egg Bhurji',
        'description': 'Scrambled eggs cooked with onions, tomatoes, and spices',
        'category': 'Breakfast',
        'price': 70.00,
        'calories': 200,
        'is_vegetarian': False,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Boiled Eggs',
        'description': 'Two hard-boiled eggs with salt and pepper',
        'category': 'Breakfast',
        'price': 30.00,
        'calories': 140,
        'is_vegetarian': False,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Bread Butter',
        'description': 'Toasted bread with butter',
        'category': 'Breakfast',
        'price': 25.00,
        'calories': 120,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    
    # SOUP
    {
        'name': 'Chicken Soup',
        'description': 'Warm and comforting chicken soup with vegetables and aromatic herbs',
        'category': 'Soup',
        'price': 90.00,
        'calories': 120,
        'is_vegetarian': False,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Tomato Soup',
        'description': 'Creamy tomato soup with fresh herbs and a touch of cream',
        'category': 'Soup',
        'price': 70.00,
        'calories': 90,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Veg Manchow Soup',
        'description': 'Spicy vegetable soup with crispy noodles',
        'category': 'Soup',
        'price': 80.00,
        'calories': 100,
        'is_vegetarian': True,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Sweet Corn Soup',
        'description': 'Creamy sweet corn soup with vegetables',
        'category': 'Soup',
        'price': 75.00,
        'calories': 95,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Hot and Sour Soup',
        'description': 'Tangy and spicy vegetable soup',
        'category': 'Soup',
        'price': 85.00,
        'calories': 110,
        'is_vegetarian': True,
        'is_spicy': True,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    
    # DESSERT
    {
        'name': 'Gulab Jamun',
        'description': 'Soft milk dumplings soaked in aromatic sugar syrup',
        'category': 'Dessert',
        'price': 40.00,
        'calories': 180,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Rasgulla',
        'description': 'Soft spongy cottage cheese balls in sugar syrup',
        'category': 'Dessert',
        'price': 35.00,
        'calories': 150,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Ice Cream',
        'description': 'Creamy vanilla ice cream topped with chocolate sauce',
        'category': 'Dessert',
        'price': 60.00,
        'calories': 250,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Chocolate Cake',
        'description': 'Rich chocolate cake with creamy frosting',
        'category': 'Dessert',
        'price': 80.00,
        'calories': 320,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Brownie',
        'description': 'Warm chocolate brownie with vanilla ice cream',
        'category': 'Dessert',
        'price': 70.00,
        'calories': 380,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Kheer',
        'description': 'Creamy rice pudding with nuts and cardamom',
        'category': 'Dessert',
        'price': 50.00,
        'calories': 200,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Halwa',
        'description': 'Sweet semolina pudding with nuts and ghee',
        'category': 'Dessert',
        'price': 45.00,
        'calories': 180,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    
    # SALAD
    {
        'name': 'Green Salad',
        'description': 'Fresh mixed greens with cucumber, tomatoes, and light dressing',
        'category': 'Salad',
        'price': 70.00,
        'calories': 80,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Caesar Salad',
        'description': 'Romaine lettuce with parmesan cheese, croutons, and Caesar dressing',
        'category': 'Salad',
        'price': 90.00,
        'calories': 140,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Greek Salad',
        'description': 'Fresh vegetables with feta cheese and olive oil dressing',
        'category': 'Salad',
        'price': 85.00,
        'calories': 120,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Chicken Salad',
        'description': 'Grilled chicken with mixed greens and light dressing',
        'category': 'Salad',
        'price': 110.00,
        'calories': 180,
        'is_vegetarian': False,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    
    # RICE ITEMS
    {
        'name': 'Steamed Rice',
        'description': 'Plain steamed basmati rice',
        'category': 'Main Course',
        'price': 60.00,
        'calories': 160,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Jeera Rice',
        'description': 'Basmati rice flavored with cumin seeds',
        'category': 'Main Course',
        'price': 80.00,
        'calories': 180,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Curd Rice',
        'description': 'Rice mixed with yogurt and spices',
        'category': 'Main Course',
        'price': 70.00,
        'calories': 170,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 50,
        'image_url': '/api/placeholder/300/200'
    }
]

try:
    # Clear existing menu items
    existing_items = db.query(MenuItem).all()
    if existing_items:
        print(f"Found {len(existing_items)} existing menu items. Clearing them...")
        db.query(MenuItem).delete()
        db.commit()
    
    # Add new menu items
    added_count = 0
    for item_data in menu_items:
        menu_item = MenuItem(
            name=item_data['name'],
            description=item_data['description'],
            category=item_data['category'],
            price=item_data['price'],
            calories=item_data['calories'],
            is_vegetarian=item_data['is_vegetarian'],
            is_spicy=item_data['is_spicy'],
            is_available=item_data['is_available'],
            image_url=item_data['image_url'],
            created_at=datetime.utcnow()
        )
        
        db.add(menu_item)
        added_count += 1
        print(f"✅ Added: {item_data['name']} - ₹{item_data['price']}")
    
    db.commit()
    
    print(f"\n🎉 Successfully added {added_count} comprehensive menu items!")
    print("\n📋 Menu Summary by Category:")
    
    # Show summary by category
    categories = {}
    for item in menu_items:
        cat = item['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for category, count in sorted(categories.items()):
        print(f"   {category}: {count} items")
    
    print(f"\n🍽️ Total Menu Items: {len(menu_items)}")
    print(f"\n🔐 Login as Super Admin to test CRUD operations:")
    print(f"   Email: superadmin@admin.com")
    print(f"   Password: admin123")
    
except Exception as e:
    print(f"❌ Error adding menu items: {e}")
    db.rollback()
finally:
    db.close()
