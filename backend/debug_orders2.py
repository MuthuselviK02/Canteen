from app.database.session import get_db
from app.models.order import Order
from datetime import datetime, timedelta

db = next(get_db())
try:
    # Check orders around Feb 4-5 to understand the issue
    ist_offset = timedelta(hours=5, minutes=30)
    
    # Simple query for orders
    orders = db.query(Order).filter(
        Order.status.in_(['completed', 'paid'])
    ).order_by(Order.created_at.desc()).limit(10).all()
    
    print(f'Found {len(orders)} recent orders')
    for order in orders:
        ist_time = order.created_at + ist_offset
        print(f'  Order: {order.created_at} (IST: {ist_time}), Status: {order.status}')
        
finally:
    db.close()
