import requests
from datetime import datetime, timedelta

# Test the fixed daily revenue endpoint
try:
    login_data = {'email': 'superadmin@admin.com', 'password': 'admin@1230'}
    login_response = requests.post('http://localhost:8002/api/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # Test the daily revenue endpoint for 1 day
        response = requests.get('http://localhost:8002/api/billing/revenue/daily?days=1', headers=headers)
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            daily_revenue = data.get('daily_revenue', [])
            print(f'Daily revenue data length: {len(daily_revenue)}')
            
            for day in daily_revenue:
                date = day.get('date')
                revenue = day.get('revenue', 0)
                orders = day.get('orders', 0)
                invoices = day.get('invoices', 0)
                print(f'  Date: {date}, Revenue: ₹{revenue:.2f}, Orders: {orders}, Invoices: {invoices}')
        else:
            print(f'Error: {response.text}')
    else:
        print('Login failed')
        
except Exception as e:
    print(f'Error: {e}')
