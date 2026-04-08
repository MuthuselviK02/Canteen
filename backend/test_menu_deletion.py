import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.services.menu_item_deletion_service import MenuItemDeletionService

db = SessionLocal()

print('🔍 === MENU ITEM DELETION SERVICE TEST ===')

# Get all menu items to see what we have
from app.models.menu import MenuItem
menu_items = db.query(MenuItem).all()

print(f'📋 Found {len(menu_items)} menu items in database')

# Show first few items
for i, item in enumerate(menu_items[:5]):
    print(f'{i+1}. {item.name} (ID: {item.id}) - Category: {item.category}')

# Check references for a specific item (let's use ID 1 if it exists)
test_item_id = 1
test_item = db.query(MenuItem).filter(MenuItem.id == test_item_id).first()

if test_item:
    print(f'\n🔍 Checking references for: {test_item.name} (ID: {test_item_id})')
    references = MenuItemDeletionService.get_menu_item_references(db, test_item_id)
    
    if 'error' not in references:
        print(f'📊 References found:')
        for ref_type, count in references['references'].items():
            print(f'  {ref_type}: {count}')
        total_refs = references['total_references']
        print(f'📈 Total references: {total_refs}')
    else:
        print(f'❌ Error: {references[\"error\"]}')
else:
    print(f'❌ Menu item with ID {test_item_id} not found')

db.close()
