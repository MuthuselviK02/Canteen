import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.menu import MenuItem
from datetime import datetime

print('=== Updating Menu Items with Missing Fields ===')

db = SessionLocal()

try:
    # Get all menu items that are missing base_prep_time
    items_to_update = db.query(MenuItem).filter(MenuItem.base_prep_time.is_(None)).all()
    
    print(f"Found {len(items_to_update)} items to update")
    
    # Default preparation times by category
    default_prep_times = {
        'Main Course': 20,
        'Breakfast': 15,
        'Soup': 10,
        'Snacks': 12,
        'Dessert': 8,
        'Beverage': 5,
        'Salad': 8
    }
    
    updated_count = 0
    for item in items_to_update:
        # Set default prep time based on category
        item.base_prep_time = default_prep_times.get(item.category, 15)
        updated_count += 1
        print(f"✅ Updated: {item.name} - Prep time: {item.base_prep_time} min")
    
    db.commit()
    
    print(f"\n🎉 Successfully updated {updated_count} menu items!")
    
    # Test the menu API
    print("\n🧪 Testing menu API...")
    available_items = db.query(MenuItem).filter(MenuItem.is_available == True).all()
    print(f"Available items in database: {len(available_items)}")
    
    if available_items:
        print("\n📋 Sample items:")
        for item in available_items[:5]:
            print(f"   - {item.name}: ₹{item.price} ({item.category}) - {item.base_prep_time} min")
    
except Exception as e:
    print(f"❌ Error updating menu items: {e}")
    db.rollback()
finally:
    db.close()
