import requests
import json

print('🔧 === DIRECT ORDER TEST ===')
print()

# Test login first
login_data = {
    "email": "superadmin@admin.com", 
    "password": "admin123"
}

try:
    login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
    if login_response.ok:
        token = login_response.json().get('access_token')
        print('✅ Login successful')
    else:
        print(f'❌ Login failed: {login_response.status_code}')
        exit()
except Exception as e:
    print(f'❌ Login error: {e}')
    exit()

print()

# Test creating order with minimal data
print('2. Testing minimal order creation...')

# Try to create order without items first
minimal_order_data = {
    "items": [
        {
            "menu_item_id": 1,
            "quantity": 1
        }
    ],
    "available_time": None
}

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

try:
    print('Sending order data:', json.dumps(minimal_order_data, indent=2))
    
    order_response = requests.post('http://localhost:8000/api/orders/', json=minimal_order_data, headers=headers)
    
    print(f'Status Code: {order_response.status_code}')
    print(f'Response Text: {order_response.text}')
    
    if order_response.ok:
        order_result = order_response.json()
        print('✅ Order placed successfully!')
        print(f'Order ID: {order_result.get("id")}')
    else:
        print('❌ Order placement failed')
        
        # Try to get more error details
        try:
            error_data = order_response.json()
            print(f'Error detail: {error_data}')
        except:
            pass

except Exception as e:
    print(f'❌ Order placement error: {e}')
    import traceback
    traceback.print_exc()

print()
print('3. Testing database connection...')
try:
    # Test if we can at least get orders (this might trigger the same error)
    orders_response = requests.get('http://localhost:8000/api/orders/', headers=headers)
    print(f'Orders endpoint status: {orders_response.status_code}')
    if orders_response.ok:
        orders = orders_response.json()
        print(f'Found {len(orders)} existing orders')
    else:
        print(f'Orders error: {orders_response.text}')
except Exception as e:
    print(f'Orders endpoint error: {e}')
