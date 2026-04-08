import requests
import json

# Login as admin
login_data = {
    'email': 'superadmin@admin.com',
    'password': 'admin123'  # Default password
}

try:
    response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
    if response.status_code == 200:
        token_data = response.json()
        token = token_data['access_token']
        print(f'✅ Login successful, got token')
        
        # Test KPI endpoint
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        kpi_response = requests.get('http://localhost:8000/api/admin/kpi/daily', headers=headers)
        
        if kpi_response.status_code == 200:
            kpi_data = kpi_response.json()
            print('✅ KPI API Response:')
            print(json.dumps(kpi_data, indent=2))
        else:
            print(f'❌ KPI API failed: {kpi_response.status_code}')
            print(kpi_response.text)
    else:
        print(f'❌ Login failed: {response.status_code}')
        print(response.text)
        
except Exception as e:
    print(f'❌ Error: {e}')
