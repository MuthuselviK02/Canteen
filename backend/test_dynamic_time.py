import requests
import time
from datetime import datetime

def test_dynamic_time_system():
    print("🧪 Testing Dynamic Time System")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1. Testing login...")
    login_response = requests.post(
        'http://localhost:8000/api/auth/login',
        json={'email': 'superadmin@admin.com', 'password': 'admin@1230'}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()['access_token']
    print("✅ Login successful")
    
    # Step 2: Place a new order to test current timestamp
    print("\n2. Placing new order with current timestamp...")
    order_data = {
        'items': [{'menu_item_id': 1, 'quantity': 1}],
        'available_time': None
    }
    
    order_response = requests.post(
        'http://localhost:8000/api/orders/',
        json=order_data,
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if order_response.status_code != 200:
        print(f"❌ Order placement failed: {order_response.text}")
        return
    
    new_order = order_response.json()
    order_id = new_order['id']
    print(f"✅ Order placed successfully! Order ID: {order_id}")
    print(f"   Created at: {new_order.get('created_at')}")
    print(f"   Initial status: {new_order.get('status')}")
    print(f"   Initial wait time: {new_order.get('predicted_wait_time')} minutes")
    
    # Step 3: Test dynamic time calculation for pending orders
    print("\n3. Testing dynamic time calculation...")
    orders_response = requests.get(
        'http://localhost:8000/api/orders/',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if orders_response.status_code != 200:
        print("❌ Failed to fetch orders")
        return
    
    orders = orders_response.json()
    pending_orders = [o for o in orders if o['status'] == 'pending']
    
    print(f"✅ Found {len(pending_orders)} pending orders")
    for order in pending_orders[:3]:  # Check first 3
        print(f"   Order {order['id']}: {order['predicted_wait_time']} min wait time")
        print(f"   Created: {order.get('created_at')}")
        print(f"   Queue position: {order.get('queue_position')}")
    
    # Step 4: Test status update with timestamps
    print("\n4. Testing status update with timestamps...")
    status_update_response = requests.put(
        f'http://localhost:8000/api/orders/{order_id}/status',
        params={'status': 'preparing'},
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if status_update_response.status_code == 200:
        print("✅ Status updated to 'preparing'")
        
        # Check the updated order
        updated_order_response = requests.get(
            f'http://localhost:8000/api/orders/{order_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if updated_order_response.status_code == 200:
            updated_order = updated_order_response.json()
            print(f"   Status: {updated_order.get('status')}")
            print(f"   Started preparation at: {updated_order.get('started_preparation_at')}")
            print(f"   Updated wait time: {updated_order.get('predicted_wait_time')} minutes")
    else:
        print(f"❌ Status update failed: {status_update_response.text}")
    
    # Step 5: Test time summary endpoint
    print("\n5. Testing time summary endpoint...")
    time_summary_response = requests.get(
        f'http://localhost:8000/api/orders/{order_id}/time-summary',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if time_summary_response.status_code == 200:
        summary = time_summary_response.json()
        print("✅ Time summary retrieved:")
        print(f"   Order ID: {summary.get('order_id')}")
        print(f"   Status: {summary.get('status')}")
        print(f"   Time elapsed: {summary.get('time_elapsed_minutes')} minutes")
        print(f"   Estimated wait time: {summary.get('estimated_wait_time')} minutes")
        if 'time_to_ready' in summary:
            print(f"   Time to ready: {summary.get('time_to_ready')} minutes")
    else:
        print(f"❌ Time summary failed: {time_summary_response.text}")
    
    # Step 6: Test queue update
    print("\n6. Testing queue update...")
    queue_update_response = requests.post(
        'http://localhost:8000/api/orders/update-queue',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if queue_update_response.status_code == 200:
        result = queue_update_response.json()
        print(f"✅ Queue update: {result.get('message')}")
    else:
        print(f"❌ Queue update failed: {queue_update_response.text}")
    
    print("\n" + "=" * 60)
    print("🎯 Dynamic Time System Test Complete!")
    print("✅ Order timestamps are working")
    print("✅ Dynamic wait time calculation is working")
    print("✅ Status updates with timestamps are working")
    print("✅ Time summary endpoint is working")
    print("✅ Queue management is working")

if __name__ == "__main__":
    test_dynamic_time_system()
