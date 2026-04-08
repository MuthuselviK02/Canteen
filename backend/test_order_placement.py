import requests
import json

print('🧪 === ORDER PLACEMENT TEST ===')
print()

# Test login first
print('1. Testing login...')
login_data = {
    "email": "superadmin@admin.com", 
    "password": "admin123"
}

try:
    login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
    if login_response.ok:
        token = login_response.json().get('access_token')
        print('✅ Login successful')
        print(f'Token: {token[:20]}...' if token else 'No token')
    else:
        print(f'❌ Login failed: {login_response.status_code}')
        print(login_response.text)
        exit()
except Exception as e:
    print(f'❌ Login error: {e}')
    exit()

print()

# Test order placement
print('2. Testing order placement...')

order_data = {
    "items": [
        {
            "menu_item_id": 1,
            "quantity": 2
        }
    ],
    "available_time": None
}

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

try:
    order_response = requests.post('http://localhost:8000/api/orders/', json=order_data, headers=headers)
    
    print(f'Status Code: {order_response.status_code}')
    print(f'Response Headers: {dict(order_response.headers)}')
    
    if order_response.ok:
        order_result = order_response.json()
        print('✅ Order placed successfully!')
        print(f'Order ID: {order_result.get("id")}')
        print(f'Predicted wait time: {order_result.get("predicted_wait_time")} minutes')
        print(f'Queue position: {order_result.get("queue_position")}')
    else:
        print('❌ Order placement failed')
        print(f'Status: {order_response.status_code}')
        print(f'Response: {order_response.text}')
        
        # Try to parse error
        try:
            error_data = order_response.json()
            print(f'Error detail: {error_data.get("detail")}')
        except:
            pass

except Exception as e:
    print(f'❌ Order placement error: {e}')

print()
print('3. Testing menu items (to verify menu_item_id)...')
try:
    menu_response = requests.get('http://localhost:8000/api/menu/')
    if menu_response.ok:
        menu_items = menu_response.json()
        print(f'✅ Found {len(menu_items)} menu items')
        if menu_items:
            print('First few items:')
            for i, item in enumerate(menu_items[:3]):
                print(f'  ID: {item.get("id")} - {item.get("name")} - ₹{item.get("price")}')
    else:
        print(f'❌ Menu fetch failed: {menu_response.status_code}')
except Exception as e:
    print(f'❌ Menu fetch error: {e}')

print()
print('🌐 Frontend should be available at: http://localhost:8081/menu')
print('Try placing an order and check the browser console for detailed error messages.')
