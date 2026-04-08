"""
Test if the billing service is updated
"""
import requests

try:
    login_data = {'email': 'superadmin@admin.com', 'password': 'admin@1230'}
    login_response = requests.post('http://localhost:8002/api/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # Test a simple endpoint to see if backend is responsive
        response = requests.get('http://localhost:8002/api/billing/settings', headers=headers)
        
        if response.status_code == 200:
            print('Backend is responsive')
            print('Settings response:', response.json())
        else:
            print(f'Settings failed: {response.status_code}')
    else:
        print('Login failed')
        
except Exception as e:
    print(f'Error: {e}')
