from app.database.session import SessionLocal
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu import MenuItem
from datetime import datetime, timedelta
from sqlalchemy import func

db = SessionLocal()

# Check recent orders and their status
print('=== RECENT ORDERS ===')
recent_orders = db.query(Order).filter(
    Order.created_at >= datetime.now() - timedelta(hours=24)
).order_by(Order.created_at.desc()).limit(10).all()

for order in recent_orders:
    print(f'Order {order.id}: Status={order.status}, Created={order.created_at}, Completed={order.completed_at}')
    
    # Check order items
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    for item in items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        item_name = menu_item.name if menu_item else "Unknown"
        print(f'  - Item: {item_name}, Qty: {item.quantity}')

print()

# Check current inventory levels
print('=== CURRENT INVENTORY LEVELS ===')
menu_items = db.query(MenuItem).limit(5).all()
for item in menu_items:
    print(f'{item.name}: Present Stock = {item.present_stocks}')

# Check completed orders today
print()
print('=== COMPLETED ORDERS TODAY ===')
today = datetime.now().date()
start_of_day = datetime.combine(today, datetime.min.time())
end_of_day = datetime.combine(today, datetime.max.time())

completed_orders = db.query(Order).filter(
    Order.completed_at.isnot(None),
    Order.completed_at >= start_of_day,
    Order.completed_at <= end_of_day
).all()

print(f'Found {len(completed_orders)} completed orders today')

# Show inventory calculation for one item
print()
print('=== INVENTORY CALCULATION EXAMPLE ===')
sample_item = db.query(MenuItem).first()
if sample_item:
    print(f'Item: {sample_item.name}')
    print(f'Present Stock: {sample_item.present_stocks}')
    
    # Calculate completed orders today
    completed_qty = db.query(func.coalesce(func.sum(OrderItem.quantity), 0))\
        .join(Order, Order.id == OrderItem.order_id)\
        .filter(
            OrderItem.menu_item_id == sample_item.id,
            Order.completed_at.isnot(None),
            Order.completed_at >= start_of_day,
            Order.completed_at <= end_of_day,
            func.lower(func.trim(Order.status)) == "completed"
        ).scalar() or 0
    
    print(f'Completed Orders Today: {completed_qty}')
    print(f'Remaining Stock: {sample_item.present_stocks - completed_qty}')

db.close()
