import urllib.request
import json

# Test login
login_data = json.dumps({'email': 'sharan@gmail.com', 'password': 'sharan@1230'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/auth/login', data=login_data, headers={'Content-Type': 'application/json'})
try:
    response = urllib.request.urlopen(req)
    print(f'Login Status: {response.getcode()}')
    data = json.loads(response.read().decode('utf-8'))
    token = data.get('access_token')
    if token:
        print('Login successful, got token')
        # Test analytics with token
        req2 = urllib.request.Request('http://localhost:8000/api/analytics/dashboard', headers={'Authorization': f'Bearer {token}'})
        response2 = urllib.request.urlopen(req2)
        print(f'Analytics Status: {response2.getcode()}')
        analytics_data = json.loads(response2.read().decode('utf-8'))
        kpi = analytics_data.get('kpi_metrics', {}).get('current_period', {})
        print(f'Orders: {kpi.get("orders", 0)}')
        print(f'Revenue: ${kpi.get("revenue", 0):.2f}')
    else:
        print('Login failed, no token')
except Exception as e:
    print(f'Error: {e}')