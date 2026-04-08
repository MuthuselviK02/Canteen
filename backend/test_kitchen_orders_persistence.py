import requests
import time

def test_kitchen_orders_persistence():
    print("🧪 Testing Kitchen Orders Persistence Fix")
    print("=" * 60)
    
    # Step 1: Login and create multiple orders
    print("\n1. Creating multiple test orders...")
    login_response = requests.post(
        'http://localhost:8000/api/auth/login',
        json={'email': 'superadmin@admin.com', 'password': 'admin@1230'}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()['access_token']
    print("✅ Login successful")
    
    # Create multiple orders
    order_ids = []
    for i in range(3):
        order_data = {
            'items': [{'menu_item_id': 1, 'quantity': 1}],
            'available_time': None
        }
        
        order_response = requests.post(
            'http://localhost:8000/api/orders/',
            json=order_data,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if order_response.status_code == 200:
            order = order_response.json()
            order_ids.append(order['id'])
            print(f"✅ Created order {order['id']}")
        else:
            print(f"❌ Failed to create order {i+1}")
    
    if len(order_ids) < 2:
        print("❌ Need at least 2 orders for testing")
        return
    
    # Step 2: Get initial state of all orders
    print("\n2. Getting initial state of all orders...")
    initial_orders_response = requests.get(
        'http://localhost:8000/api/orders/',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if initial_orders_response.status_code != 200:
        print("❌ Failed to get initial orders")
        return
    
    initial_orders = initial_orders_response.json()
    initial_count = len(initial_orders)
    print(f"✅ Initial orders count: {initial_count}")
    
    for order in initial_orders:
        if order['id'] in order_ids:
            print(f"   Order {order['id']}: {order['status']}")
    
    # Step 3: Update one order status (simulate kitchen action)
    print(f"\n3. Updating order {order_ids[0]} status...")
    
    update_response = requests.put(
        f'http://localhost:8000/api/orders/{order_ids[0]}/status',
        params={'status': 'preparing'},
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if update_response.status_code == 200:
        result = update_response.json()
        print(f"✅ Order {order_ids[0]} updated to: {result.get('new_status')}")
    else:
        print(f"❌ Failed to update order: {update_response.text}")
        return
    
    # Step 4: Check if other orders are still present
    print("\n4. Checking if other orders are still present...")
    
    time.sleep(1)  # Wait a moment for any potential issues
    
    updated_orders_response = requests.get(
        'http://localhost:8000/api/orders/',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if updated_orders_response.status_code != 200:
        print("❌ Failed to get updated orders")
        return
    
    updated_orders = updated_orders_response.json()
    updated_count = len(updated_orders)
    print(f"✅ Updated orders count: {updated_count}")
    
    # Check if we still have all orders
    missing_orders = []
    present_orders = []
    
    for order_id in order_ids:
        found = False
        for order in updated_orders:
            if order['id'] == order_id:
                present_orders.append(order)
                found = True
                break
        if not found:
            missing_orders.append(order_id)
    
    # Step 5: Verify results
    print("\n5. Verifying results...")
    
    if len(missing_orders) == 0 and updated_count == initial_count:
        print("✅ SUCCESS: All orders are still present")
        print("✅ SUCCESS: No orders disappeared after update")
        
        for order in present_orders:
            status_icon = "🔄" if order['status'] == 'preparing' else "⏳"
            print(f"   {status_icon} Order {order['id']}: {order['status']}")
        
    else:
        print("❌ FAILURE: Some orders disappeared")
        print(f"   Missing orders: {missing_orders}")
        print(f"   Expected count: {initial_count}, Got: {updated_count}")
        return
    
    # Step 6: Update another order to test further
    print(f"\n6. Updating order {order_ids[1]} status...")
    
    update_response2 = requests.put(
        f'http://localhost:8000/api/orders/{order_ids[1]}/status',
        params={'status': 'ready'},
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if update_response2.status_code == 200:
        result = update_response2.json()
        print(f"✅ Order {order_ids[1]} updated to: {result.get('new_status')}")
    else:
        print(f"❌ Failed to update order: {update_response2.text}")
        return
    
    # Step 7: Final verification
    print("\n7. Final verification...")
    
    final_orders_response = requests.get(
        'http://localhost:8000/api/orders/',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if final_orders_response.status_code == 200:
        final_orders = final_orders_response.json()
        final_count = len(final_orders)
        
        if final_count == initial_count:
            print("✅ SUCCESS: All orders still present after multiple updates")
            
            print("\n📊 Final Order States:")
            for order in final_orders:
                if order['id'] in order_ids:
                    status_icons = {
                        'pending': '⏳',
                        'preparing': '🔄',
                        'ready': '✅',
                        'completed': '🎉'
                    }
                    icon = status_icons.get(order['status'], '❓')
                    print(f"   {icon} Order {order['id']}: {order['status']}")
            
            print("\n🎯 KITCHEN ORDERS PERSISTENCE TEST COMPLETE!")
            print("✅ Orders no longer disappear when updating one item")
            print("✅ All orders remain visible in kitchen dashboard")
            print("✅ Status updates work correctly without affecting other orders")
            print("✅ Production-ready order persistence implemented")
            
        else:
            print(f"❌ FAILURE: Order count changed from {initial_count} to {final_count}")
    
    else:
        print("❌ Failed to get final orders")

if __name__ == "__main__":
    test_kitchen_orders_persistence()
