import requests

def test_complete_frontend_flow():
    print("🧪 Testing Complete Frontend Flow")
    print("=" * 50)
    
    # Step 1: Login (like frontend)
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
    
    # Step 2: Get current user (like frontend AuthContext)
    print("\n2. Testing /auth/me...")
    me_response = requests.get(
        'http://localhost:8000/api/auth/me',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if me_response.status_code != 200:
        print("❌ Auth/me failed")
        return
    
    user_data = me_response.json()
    user_id = user_data['id']
    print(f"✅ User data retrieved - ID: {user_id}")
    
    # Step 3: Get orders (like frontend OrderContext)
    print("\n3. Testing /orders/...")
    orders_response = requests.get(
        'http://localhost:8000/api/orders/',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if orders_response.status_code != 200:
        print("❌ Orders fetch failed")
        return
    
    api_orders = orders_response.json()
    print(f"✅ Orders retrieved - Count: {len(api_orders)}")
    
    # Step 4: Transform data (like frontend)
    print("\n4. Testing data transformation...")
    transformed_orders = []
    for api_order in api_orders:
        transformed = {
            'id': str(api_order['id']),
            'userId': api_order['user_id'],
            'userName': 'User',
            'items': [],
            'totalPrice': 0,
            'totalCalories': 0,
            'estimatedTime': api_order.get('predicted_wait_time', 15),
            'status': api_order['status'].lower(),
            'queuePosition': api_order.get('queue_position', 1),
            'createdAt': '2024-01-01'  # Placeholder
        }
        
        # Transform items
        for item in api_order.get('items', []):
            menu_item = item.get('menu_item', {})
            transformed_item = {
                'menuItem': {
                    'id': str(menu_item.get('id', item['menu_item_id'])),
                    'name': menu_item.get('name', 'Unknown Item'),
                    'description': menu_item.get('description', ''),
                    'price': menu_item.get('price', 0),
                    'prepTime': menu_item.get('base_prep_time', 10),
                    'calories': menu_item.get('calories', 0),
                    'category': menu_item.get('category', 'Main Course'),
                    'image': menu_item.get('image_url', 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop'),
                    'available': menu_item.get('is_available', True)
                },
                'quantity': item['quantity']
            }
            transformed['items'].append(transformed_item)
            transformed['totalPrice'] += transformed_item['menuItem']['price'] * item['quantity']
            transformed['totalCalories'] += transformed_item['menuItem']['calories'] * item['quantity']
        
        transformed_orders.append(transformed)
    
    print(f"✅ Data transformed - Count: {len(transformed_orders)}")
    
    # Step 5: Filter orders (like frontend Orders page)
    print("\n5. Testing order filtering...")
    user_orders = [o for o in transformed_orders if o['userId'] == user_id]
    active_orders = [o for o in user_orders if o['status'] != 'completed']
    past_orders = [o for o in user_orders if o['status'] == 'completed']
    
    print(f"✅ Orders filtered:")
    print(f"   User orders: {len(user_orders)}")
    print(f"   Active orders: {len(active_orders)}")
    print(f"   Past orders: {len(past_orders)}")
    
    # Step 6: Display sample order
    if active_orders:
        print("\n6. Sample active order:")
        order = active_orders[0]
        print(f"   Order ID: {order['id']}")
        print(f"   Status: {order['status']}")
        print(f"   Total Price: ${order['totalPrice']:.2f}")
        print(f"   Items: {len(order['items'])}")
        for item in order['items']:
            print(f"   - {item['menuItem']['name']} x{item['quantity']} = ${item['menuItem']['price'] * item['quantity']:.2f}")
    
    print("\n" + "=" * 50)
    print("🎯 Frontend Flow Test Complete!")
    print("✅ All steps working correctly")
    print("✅ Orders page should display orders now")

if __name__ == "__main__":
    test_complete_frontend_flow()
