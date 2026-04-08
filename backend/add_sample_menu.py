import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.menu import MenuItem
from datetime import datetime

print('=== Adding Sample Menu Items for Testing ===')

db = SessionLocal()

# Sample menu items for testing CRUD operations
menu_items = [
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
        'name': 'Masala Dosa',
        'description': 'Crispy rice crepe filled with spiced potato mixture, served with sambar and chutney',
        'category': 'Breakfast',
        'price': 120.00,
        'calories': 280,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 30,
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
        'present_stocks': 30,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Chicken Soup',
        'description': 'Warm and comforting chicken soup with vegetables and aromatic herbs',
        'category': 'Soup',
        'price': 90.00,
        'calories': 120,
        'is_vegetarian': False,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 30,
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
        'present_stocks': 30,
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
        'present_stocks': 30,
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
        'present_stocks': 30,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'French Fries',
        'description': 'Crispy golden potato fries seasoned with salt and herbs',
        'category': 'Snacks',
        'price': 50.00,
        'calories': 220,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 30,
        'image_url': '/api/placeholder/300/200'
    },
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
        'name': 'Gulab Jamun',
        'description': 'Soft milk dumplings soaked in aromatic sugar syrup',
        'category': 'Dessert',
        'price': 40.00,
        'calories': 180,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 30,
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
        'present_stocks': 30,
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
        'present_stocks': 30,
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
        'present_stocks': 30,
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
        'present_stocks': 30,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Cold Coffee',
        'description': 'Chilled coffee with milk, ice, and a touch of chocolate',
        'category': 'Beverage',
        'price': 60.00,
        'calories': 150,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 30,
        'image_url': '/api/placeholder/300/200'
    },
    {
        'name': 'Green Salad',
        'description': 'Fresh mixed greens with cucumber, tomatoes, and light dressing',
        'category': 'Salad',
        'price': 70.00,
        'calories': 80,
        'is_vegetarian': True,
        'is_spicy': False,
        'is_available': True,
        'present_stocks': 30,
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
        'present_stocks': 30,
        'image_url': '/api/placeholder/300/200'
    }
]

try:
    # Clear existing menu items (optional - comment out if you want to keep existing)
    existing_items = db.query(MenuItem).all()
    if existing_items:
        print(f"Found {len(existing_items)} existing menu items. Clearing them...")
        db.query(MenuItem).delete()
        db.commit()
    
    # Add new menu items
    added_count = 0
    for item_data in menu_items:
        # Check if item already exists
        existing = db.query(MenuItem).filter(MenuItem.name == item_data['name']).first()
        if existing:
            print(f"⚠️  Item '{item_data['name']}' already exists, skipping...")
            continue
        
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
    
    print(f"\n🎉 Successfully added {added_count} menu items to the database!")
    print("\n📋 Menu Summary:")
    
    # Show summary by category
    categories = {}
    for item in menu_items:
        cat = item['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for category, count in categories.items():
        print(f"   {category}: {count} items")
    
    print(f"\n🔐 Login Credentials:")
    print(f"   Email: superadmin@admin.com")
    print(f"   Password: admin123")
    print(f"\n📝 You can now test CRUD operations in Menu Management!")
    
except Exception as e:
    print(f"❌ Error adding menu items: {e}")
    db.rollback()
finally:
    db.close()
