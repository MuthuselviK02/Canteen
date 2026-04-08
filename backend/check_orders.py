import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.order import Order
from datetime import datetime

print('📊 === CHECKING EXISTING ORDERS ===')
print()

db = SessionLocal()
orders = db.query(Order).limit(3).all()

if not orders:
    print('No orders found in database')
    print('Creating a test order...')
    
    # Create a test order with current timestamp
    test_order = Order(
        user_id=1,
        status='pending',
        queue_position=1,
        predicted_wait_time=15,
        total_amount=150.0,
        created_at=datetime.utcnow()
    )
    
    db.add(test_order)
    db.commit()
    
    print('Test order created with ID:', test_order.id)
    print('Created at (UTC):', test_order.created_at)
    
    # Test IST conversion
    utc_time = test_order.created_at
    ist_offset = 5.5 * 60 * 60 * 1000
    ist_time = datetime.fromtimestamp((utc_time.timestamp() * 1000 + ist_offset) / 1000)
    
    print('Should display as IST:', ist_time.strftime('%I:%M %p'))
    
else:
    print(f'Found {len(orders)} orders:')
    for order in orders:
        print(f'Order #{order.id}:')
        print(f'  Status: {order.status}')
        print(f'  Created At (UTC): {order.created_at}')
        
        # Test IST conversion
        utc_time = order.created_at
        ist_offset = 5.5 * 60 * 60 * 1000
        ist_time = datetime.fromtimestamp((utc_time.timestamp() * 1000 + ist_offset) / 1000)
        
        print(f'  Should display as IST: {ist_time.strftime("%I:%M %p")}')
        print()

db.close()

print('🌐 Access the orders page at: http://localhost:8081/orders')
print('Check if the times are displayed correctly in IST')
