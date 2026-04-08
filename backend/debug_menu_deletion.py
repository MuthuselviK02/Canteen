import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.menu import MenuItem

db = SessionLocal()

try:
    menu_items = db.query(MenuItem).all()
    print(f'Found {len(menu_items)} menu items')
    
    if menu_items:
        first_item = menu_items[0]
        print(f'First item: {first_item.name} (ID: {first_item.id})')
        
        # Test the deletion service import
        from app.services.menu_item_deletion_service import MenuItemDeletionService
        print('✅ Import successful')
        
        # Test getting references
        references = MenuItemDeletionService.get_menu_item_references(db, first_item.id)
        print(f'References: {references}')
    else:
        print('No menu items found')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

finally:
    db.close()
