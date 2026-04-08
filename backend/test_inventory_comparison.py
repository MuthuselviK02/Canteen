import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.services.inventory_service import get_inventory_dashboard
from app.services.realtime_inventory_service import RealTimeInventoryService
from datetime import datetime

db = SessionLocal()

print('=== COMPARING INVENTORY CALCULATIONS ===')

# Get today's date range
today = datetime.now().date()
start_dt = datetime.combine(today, datetime.min.time())
end_dt = datetime.combine(today, datetime.max.time())

# Get regular dashboard calculation
kpis, items = get_inventory_dashboard(db, start_dt, end_dt)

# Get real-time inventory status
real_time_status = RealTimeInventoryService.get_current_inventory_status(db)

print('=== DASHBOARD vs REAL-TIME COMPARISON ===')
for item in items[:5]:
    item_id = item['item_id']
    dashboard_stock = item['remaining_stock']
    real_time_stock = real_time_status.get(item_id, {}).get('present_stock', 0)
    difference = real_time_stock - dashboard_stock
    
    print(f'{item["item_name"]}:')
    print(f'  Dashboard: {dashboard_stock}')
    print(f'  Real-time: {real_time_stock}')
    print(f'  Difference: {difference}')
    print()

# Check specific items that were updated
print('=== SPECIFIC UPDATED ITEMS ===')
noodles_id = None
orange_juice_id = None

for item_id, data in real_time_status.items():
    if 'Noodles' in data['name']:
        noodles_id = item_id
    if 'Orange Juice' in data['name']:
        orange_juice_id = item_id

if noodles_id:
    noodles_dashboard = next((item for item in items if item['item_id'] == noodles_id), None)
    if noodles_dashboard:
        print(f'Noodles - Dashboard: {noodles_dashboard["remaining_stock"]}, Real-time: {real_time_status[noodles_id]["present_stock"]}')

if orange_juice_id:
    orange_dashboard = next((item for item in items if item['item_id'] == orange_juice_id), None)
    if orange_dashboard:
        print(f'Orange Juice - Dashboard: {orange_dashboard["remaining_stock"]}, Real-time: {real_time_status[orange_juice_id]["present_stock"]}')

db.close()
