import requests
import json

print('🧪 Testing Kitchen Analytics Button Functionality...')
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

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

print()
print('1. Testing Kitchen Analytics API (for Show Analytics button)...')
try:
    response = requests.get('http://localhost:8000/api/analytics/kitchen', headers=headers)
    
    if response.ok:
        data = response.json()
        print('✅ Kitchen Analytics API working correctly')
        print(f'   Data received: {bool(data)}')
        print(f'   Keys: {list(data.keys())}')
        print(f'   Active orders: {data.get("current_queue", {}).get("total_active_orders", 0)}')
        print(f'   Efficiency score: {data.get("efficiency", {}).get("efficiency_score", 0)}/100')
        print(f'   Alerts: {data.get("alerts", {})}')
    else:
        print(f'❌ Kitchen Analytics API failed: {response.status_code}')
        print(f'   Response: {response.text}')
except Exception as e:
    print(f'❌ Kitchen Analytics API error: {e}')

print()
print('2. Testing with different user roles...')

# Test with kitchen staff role (if available)
try:
    # Try to get user info first
    user_response = requests.get('http://localhost:8000/api/analytics/debug/user', headers=headers)
    if user_response.ok:
        user_info = user_response.json()
        print(f'✅ Current user: {user_info.get("email")} (Role: {user_info.get("role")})')
        
        # Check if this user should have access to kitchen analytics
        if user_info.get('role') in ['KITCHEN', 'STAFF', 'SUPER_ADMIN', 'ADMIN']:
            print('✅ User has permission to access kitchen analytics')
        else:
            print('❌ User does not have kitchen analytics permission')
    else:
        print('❌ Could not verify user permissions')
except Exception as e:
    print(f'❌ User permission check error: {e}')

print()
print('3. Simulating Frontend "Show Analytics" Button Click...')
print('   When you click "Show Analytics", the frontend should:')
print('   1. Set showAnalytics = true')
print('   2. Render the KitchenAnalytics component')
print('   3. Call fetchKitchenAnalytics() function')
print('   4. Display the analytics data')
print()
print('🔍 Debugging Steps if Analytics Not Showing:')
print('   1. Check browser console for JavaScript errors')
print('   2. Verify the button click is changing showAnalytics state')
print('   3. Check if KitchenAnalytics component is mounting')
print('   4. Verify API calls are being made in Network tab')
print('   5. Check if there are any authentication issues')

print()
print('🌐 Test the Kitchen Page:')
print('   1. Go to: http://localhost:8081/kitchen')
print('   2. Click the "Show Analytics" button')
print('   3. Check if analytics appear below the header')
print('   4. Look for any error messages or loading states')

print()
print('📊 Expected Analytics Display:')
print('   - Real-time kitchen status (Normal/Warning/Critical)')
print('   - Active queue metrics')
print('   - Preparation time statistics')
print('   - Efficiency score and performance metrics')
print('   - Hourly performance chart')
print('   - Alert notifications (if any)')
