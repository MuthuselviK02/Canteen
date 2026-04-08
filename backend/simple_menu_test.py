import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.menu import MenuItem
from app.models.inventory import InventoryLog, InventoryStockUpdate

db = SessionLocal()

print('🔍 === SIMPLE MENU DELETION TEST ===')

try:
    # Get a menu item
    menu_item = db.query(MenuItem).first()
    if menu_item:
        print(f'Testing with: {menu_item.name} (ID: {menu_item.id})')
        
        # Count related records manually
        from app.models.order_item import OrderItem
        order_items_count = db.query(OrderItem).filter(OrderItem.menu_item_id == menu_item.id).count()
        inventory_logs_count = db.query(InventoryLog).filter(InventoryLog.menu_item_id == menu_item.id).count()
        stock_updates_count = db.query(InventoryStockUpdate).filter(InventoryStockUpdate.menu_item_id == menu_item.id).count()
        
        print(f'Order items: {order_items_count}')
        print(f'Inventory logs: {inventory_logs_count}')
        print(f'Stock updates: {stock_updates_count}')
        
        # Test deletion service with a simple approach
        from app.services.menu_item_deletion_service import MenuItemDeletionService
        
        # Just test the reference counting part
        references = MenuItemDeletionService.get_menu_item_references(db, menu_item.id)
        print(f'References result: {references}')
        
    else:
        print('No menu items found')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

finally:
    db.close()
