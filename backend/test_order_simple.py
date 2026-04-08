import requests

# Test login first
login_data = {'email': 'superadmin@admin.com', 'password': 'admin123'}
login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
token = login_response.json().get('access_token')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Test simple order placement
order_data = {
    "items": [
        {
            "menu_item_id": 1,
            "quantity": 1
        }
    ],
    "available_time": None
}

print('Testing order placement...')
response = requests.post('http://localhost:8000/api/orders/', json=order_data, headers=headers)
print(f'Status: {response.status_code}')
if response.ok:
    print('Success:', response.json())
else:
    print('Error:', response.text)
