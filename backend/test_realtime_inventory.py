import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.services.realtime_inventory_service import RealTimeInventoryService
from datetime import datetime

db = SessionLocal()

print('=== TESTING REAL-TIME INVENTORY SYSTEM ===')

# Test with a recent completed order
# Order 15 was completed today
test_order_id = 15

print(f'Testing inventory update for order {test_order_id}')

try:
    RealTimeInventoryService.update_inventory_on_order_completion(db, test_order_id)
    print('✅ Real-time inventory update successful!')
except Exception as e:
    print(f'❌ Error: {e}')

# Check current inventory status
print('\n=== CURRENT INVENTORY STATUS ===')
status = RealTimeInventoryService.get_current_inventory_status(db)

# Show a few items
for i, (item_id, data) in enumerate(list(status.items())[:5]):
    print(f'{data["name"]}: {data["present_stock"]} units')

db.close()
