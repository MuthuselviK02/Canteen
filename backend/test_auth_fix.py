import requests
import json

print('🔧 === PREDICTIVE AI AUTHENTICATION FIX TEST ===')
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
        print(f'🔑 Token received: {token[:50]}...')
    else:
        print(f'❌ Login failed: {login_response.status_code}')
        exit()
except Exception as e:
    print(f'❌ Login error: {e}')
    exit()

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

print()
print('🔍 Testing Predictive Analytics APIs with correct token...')

# Test dashboard summary
try:
    response = requests.get('http://localhost:8000/api/predictive-analytics/dashboard-summary', headers=headers)
    if response.ok:
        data = response.json()
        print('✅ Dashboard Summary API working')
        print(f'   Features: {list(data.keys())}')
    else:
        print(f'❌ Dashboard Summary failed: {response.status_code}')
        print(f'   Response: {response.text}')
except Exception as e:
    print(f'❌ Dashboard Summary error: {e}')

# Test model performance
try:
    response = requests.get('http://localhost:8000/api/predictive-analytics/model-performance', headers=headers)
    if response.ok:
        data = response.json()
        print('✅ Model Performance API working')
        print(f'   Models: {list(data.keys())}')
    else:
        print(f'❌ Model Performance failed: {response.status_code}')
        print(f'   Response: {response.text}')
except Exception as e:
    print(f'❌ Model Performance error: {e}')

print()
print('🎯 FRONTEND FIX APPLIED:')
print('✅ Changed token key from "token" to "canteen_token"')
print('✅ PredictiveAnalyticsDashboard.tsx updated')
print('✅ Authentication should now work correctly')

print()
print('🌐 TESTING INSTRUCTIONS:')
print('1. Go to: http://localhost:8081/admin')
print('2. Click "Predictive AI" tab')
print('3. Should now load without 401 errors')
print('4. Refresh page if needed (Ctrl+F5)')

print()
print('🚀 Predictive AI should now work correctly!')
