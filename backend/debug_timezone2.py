import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu import MenuItem
from datetime import datetime, timedelta
from sqlalchemy import func

db = SessionLocal()

print('=== TIMEZONE DEBUG ===')
today = datetime.now().date()
start_of_day = datetime.combine(today, datetime.min.time())
end_of_day = datetime.combine(today, datetime.max.time())

print(f'Today: {today}')
print(f'Start of day: {start_of_day}')
print(f'End of day: {end_of_day}')
print(f'Current UTC time: {datetime.utcnow()}')

# Check all completed orders with their completion times
print('\n=== ALL COMPLETED ORDERS WITH TIMES ===')
all_completed = db.query(Order).filter(
    Order.completed_at.isnot(None)
).order_by(Order.completed_at.desc()).limit(10).all()

for order in all_completed:
    print(f'Order {order.id}: Status={order.status}, Completed={order.completed_at}')

# Check specific items that were consumed
print('\n=== SPECIFIC ITEM ANALYSIS ===')
# Check Mango Lassi
mango_lassi = db.query(MenuItem).filter(MenuItem.name.like('%Mango Lassi%')).first()
if mango_lassi:
    print(f'Mango Lassi ID: {mango_lassi.id}')
    
    # Check completed orders for this item
    completed_qty = db.query(func.coalesce(func.sum(OrderItem.quantity), 0))\
        .join(Order, Order.id == OrderItem.order_id)\
        .filter(
            OrderItem.menu_item_id == mango_lassi.id,
            Order.completed_at.isnot(None),
            Order.completed_at >= start_of_day,
            Order.completed_at <= end_of_day,
            func.lower(func.trim(Order.status)) == 'completed'
        ).scalar() or 0
    
    print(f'Mango Lassi completed quantity today: {completed_qty}')
    
    # Check all orders for this item (not time-filtered)
    all_qty = db.query(func.coalesce(func.sum(OrderItem.quantity), 0))\
        .join(Order, Order.id == OrderItem.order_id)\
        .filter(
            OrderItem.menu_item_id == mango_lassi.id,
            func.lower(func.trim(Order.status)) == 'completed'
        ).scalar() or 0
    
    print(f'Mango Lassi total completed quantity: {all_qty}')

db.close()
