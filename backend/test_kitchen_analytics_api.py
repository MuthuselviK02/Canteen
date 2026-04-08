import requests
import json

print('🔍 Testing Kitchen Analytics API...')

# Test kitchen analytics API directly
login_data = {'email': 'superadmin@admin.com', 'password': 'admin123'}

try:
    login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
    if login_response.ok:
        token = login_response.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # Test kitchen analytics
        response = requests.get('http://localhost:8000/api/analytics/kitchen', headers=headers)
        print(f'Kitchen Analytics Status: {response.status_code}')
        if response.ok:
            data = response.json()
            print(f'Kitchen Analytics Data Keys: {list(data.keys())}')
            print(f'Today stats: {data.get("today_stats", {})}')
            print(f'Current queue: {data.get("current_queue", {})}')
            print('✅ Kitchen Analytics API working')
        else:
            print(f'❌ Error: {response.text}')
    else:
        print('❌ Login failed')
except Exception as e:
    print(f'❌ Error: {e}')
