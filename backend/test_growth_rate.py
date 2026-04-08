import requests
from datetime import datetime, timedelta

# Test the revenue summary endpoint specifically for growth_rate
try:
    login_data = {'email': 'superadmin@admin.com', 'password': 'admin@1230'}
    login_response = requests.post('http://localhost:8002/api/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # Test today's revenue summary
        now = datetime.utcnow()
        ist_offset = timedelta(hours=5, minutes=30)
        ist_now = now + ist_offset
        today_str = ist_now.strftime('%Y-%m-%d')
        
        response = requests.get(
            f'http://localhost:8002/api/billing/revenue/summary?start_date={today_str}&end_date={today_str}',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            summary = data.get('summary', {})
            print('Revenue Summary Response:')
            print(f'  Total Revenue: {summary.get("total_revenue", 0):.2f}')
            print(f'  Total Invoices: {summary.get("total_invoices", 0)}')
            print(f'  Growth Rate: {summary.get("growth_rate", "Not Found")}')
        else:
            print(f'Error: {response.status_code} - {response.text}')
    else:
        print('Login failed')
        
except Exception as e:
    print(f'Error: {e}')
