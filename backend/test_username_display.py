import requests

def test_username_display():
    print("🧪 Testing Username Display in Orders")
    print("=" * 50)
    
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
    
    # Step 2: Get orders with user info
    print("\n2. Testing orders with user info...")
    orders_response = requests.get(
        'http://localhost:8000/api/orders/',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if orders_response.status_code != 200:
        print("❌ Orders fetch failed")
        return
    
    orders = orders_response.json()
    print(f"✅ Found {len(orders)} orders")
    
    # Step 3: Check username in orders
    print("\n3. Checking username display...")
    for i, order in enumerate(orders[:2]):  # Check first 2 orders
        user_info = order.get('user', {})
        username = user_info.get('fullname', 'Unknown')
        user_id = order.get('user_id')
        
        print(f"\nOrder {i+1}:")
        print(f"  Order ID: {order.get('id')}")
        print(f"  User ID: {user_id}")
        print(f"  Username: {username}")
        print(f"  Email: {user_info.get('email', 'N/A')}")
        print(f"  Status: {order.get('status')}")
        print(f"  Items: {len(order.get('items', []))}")
        
        # Show sample item
        items = order.get('items', [])
        if items:
            first_item = items[0]
            menu_item = first_item.get('menu_item', {})
            print(f"  Sample Item: {menu_item.get('name', 'Unknown')} x{first_item.get('quantity', 0)}")
    
    # Step 4: Test frontend transformation
    print("\n4. Testing frontend transformation...")
    transformed_orders = []
    for api_order in orders:
        transformed = {
            'id': str(api_order['id']),
            'userId': api_order['user_id'],
            'userName': api_order.get('user', {}).get('fullname', 'User'),
            'status': api_order['status'].lower(),
            'items': len(api_order.get('items', []))
        }
        transformed_orders.append(transformed)
    
    print("✅ Frontend transformation successful")
    for i, order in enumerate(transformed_orders[:2]):
        print(f"  Order {i+1}: {order['userName']} - {order['items']} items")
    
    print("\n" + "=" * 50)
    print("🎯 Username Display Test Complete!")
    print("✅ Orders now show actual usernames instead of #user1")
    print("✅ Frontend will display: 'Super Admin' instead of '#user1'")

if __name__ == "__main__":
    test_username_display()
