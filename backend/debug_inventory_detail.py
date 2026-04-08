import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu import MenuItem
from app.services.inventory_service import get_inventory_dashboard
from datetime import datetime, timedelta
from sqlalchemy import func

db = SessionLocal()

print('=== DETAILED ORDER ANALYSIS ===')
today = datetime.now().date()
start_of_day = datetime.combine(today, datetime.min.time())
end_of_day = datetime.combine(today, datetime.max.time())

# Get completed orders with items
completed_orders = db.query(Order).filter(
    Order.completed_at.isnot(None),
    Order.completed_at >= start_of_day,
    Order.completed_at <= end_of_day,
    func.lower(func.trim(Order.status)) == 'completed'
).all()

print(f'Found {len(completed_orders)} completed orders today')

# Group by menu item to see total quantities
item_totals = {}
for order in completed_orders:
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    for item in items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        if menu_item:
            item_name = menu_item.name
            if item_name not in item_totals:
                item_totals[item_name] = {'quantity': 0, 'stock': menu_item.present_stocks}
            item_totals[item_name]['quantity'] += item.quantity

print('\n=== ITEM CONSUMPTION TODAY ===')
for item_name, data in item_totals.items():
    print(f'{item_name}: Consumed {data["quantity"]}, Present Stock {data["stock"]}')

# Test inventory dashboard calculation
print('\n=== INVENTORY DASHBOARD CALCULATION ===')
kpis, items = get_inventory_dashboard(db, start_of_day, end_of_day)

print(f'Total Items: {kpis["total_items"]}')
print(f'Well Stocked: {kpis["well_stocked"]}')
print(f'Needs Restocking: {kpis["needs_restocking"]}')
print(f'Out of Stock: {kpis["out_of_stock"]}')
print(f'No Forecast: {kpis["no_forecast"]}')

print('\n=== SAMPLE INVENTORY ITEMS ===')
for item in items[:3]:
    print(f'{item["item_name"]}:')
    print(f'  Opening Stock: {item["opening_stock"]}')
    print(f'  Completed Orders: {item["completed_orders_today"]}')
    print(f'  Remaining Stock: {item["remaining_stock"]}')
    print(f'  Status: {item["inventory_status"]}')

db.close()
