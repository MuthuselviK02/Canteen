import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu import MenuItem
from app.services.inventory_service import _sum_completed_order_quantity
from datetime import datetime, timedelta
from sqlalchemy import func

db = SessionLocal()

today = datetime.now().date()
start_of_day = datetime.combine(today, datetime.min.time())
end_of_day = datetime.combine(today, datetime.max.time())

print('=== TESTING INVENTORY CALCULATION FOR SPECIFIC ITEMS ===')

# Test Mango Lassi (ID 19) - we know this had 2 orders today
mango_lassi_id = 19
completed_qty = _sum_completed_order_quantity(db, mango_lassi_id, start_of_day, end_of_day)
print(f'Mango Lassi (ID {mango_lassi_id}): Completed orders today = {completed_qty}')

# Test Butter Chicken (should be in inventory)
butter_chicken = db.query(MenuItem).filter(MenuItem.name.like('%Butter Chicken%')).first()
if butter_chicken:
    completed_qty = _sum_completed_order_quantity(db, butter_chicken.id, start_of_day, end_of_day)
    print(f'Butter Chicken (ID {butter_chicken.id}): Completed orders today = {completed_qty}')
    print(f'Butter Chicken present_stocks: {butter_chicken.present_stocks}')

# Test a few more items
print('\n=== ALL ITEMS WITH COMPLETED ORDERS TODAY ===')
items_with_orders = db.query(OrderItem.menu_item_id, func.sum(OrderItem.quantity))\
    .join(Order, Order.id == OrderItem.order_id)\
    .filter(
        Order.completed_at.isnot(None),
        Order.completed_at >= start_of_day,
        Order.completed_at <= end_of_day,
        func.lower(func.trim(Order.status)) == 'completed'
    )\
    .group_by(OrderItem.menu_item_id)\
    .all()

for item_id, total_qty in items_with_orders:
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if menu_item:
        print(f'{menu_item.name} (ID {item_id}): {total_qty} units')

db.close()
