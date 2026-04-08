import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.services.order_service import create_order
from app.models.order_item import OrderItem

print('🔧 === SIMPLIFIED ORDER TEST ===')
print()

db = SessionLocal()

try:
    print('1. Testing basic order creation...')
    
    # Test creating a simple order without items first
    order = create_order(
        db=db,
        user_id=1,
        queue_position=1,
        predicted_time=15
    )
    
    print(f'✅ Order created successfully: ID {order.id}')
    print(f'   User ID: {order.user_id}')
    print(f'   Status: {order.status}')
    print(f'   Queue Position: {order.queue_position}')
    print(f'   Predicted Wait Time: {order.predicted_wait_time}')
    
    print()
    print('2. Testing order item creation...')
    
    # Test creating an order item
    order_item = OrderItem(
        order_id=order.id,
        menu_item_id=1,
        quantity=2
    )
    
    db.add(order_item)
    db.commit()
    db.refresh(order_item)
    
    print(f'✅ Order item created successfully: ID {order_item.id}')
    print(f'   Order ID: {order_item.order_id}')
    print(f'   Menu Item ID: {order_item.menu_item_id}')
    print(f'   Quantity: {order_item.quantity}')
    
    print()
    print('3. Testing order retrieval...')
    
    # Test getting the order with items
    from app.services.order_service import get_user_orders_with_items
    orders = get_user_orders_with_items(db, user_id=1)
    
    print(f'✅ Retrieved {len(orders)} orders for user 1')
    if orders:
        order = orders[0]
        print(f'   First order: {len(order.items)} items')
        print(f'   Status: {order.status}')
        print(f'   Wait time: {order.predicted_wait_time}')
    
    print()
    print('✅ All basic order operations working!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

finally:
    db.close()
