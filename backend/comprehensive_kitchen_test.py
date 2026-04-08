import requests
import json

print('🔧 === COMPREHENSIVE KITCHEN ANALYTICS FIX TEST ===')
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
print('🧪 Testing Backend API...')
try:
    response = requests.get('http://localhost:8000/api/analytics/kitchen', headers=headers)
    
    if response.ok:
        data = response.json()
        print('✅ Backend API working')
        print(f'   Active orders: {data.get("current_queue", {}).get("total_active_orders", 0)}')
        print(f'   Data structure: {list(data.keys())}')
    else:
        print(f'❌ Backend API failed: {response.status_code}')
        print(f'   Response: {response.text}')
except Exception as e:
    print(f'❌ Backend API error: {e}')

print()
print('🎯 FRONTEND TESTING INSTRUCTIONS:')
print('1. Open: http://localhost:8081/kitchen')
print('2. Open browser console (F12)')
print('3. Click "Show Analytics" button')
print('4. Check console logs for:')
print('   - "🔍 Analytics button clicked" message')
print('   - "📊 showAnalytics state changed" message')
print('   - Any JavaScript errors')
print()
print('5. Look for debug panel (bottom-right corner) showing:')
print('   - Component: KitchenAnalyticsMinimal')
print('   - Data Available: Yes')
print('   - Orders Count: [number]')
print('   - Active Orders: [number]')

print()
print('🔍 EXPECTED BEHAVIOR WITH MINIMAL COMPONENT:')
print('✅ Button toggles between "Show Analytics" and "Hide Analytics"')
print('✅ Console logs button clicks and state changes')
print('✅ Debug panel shows real-time information')
print('✅ Analytics display with:')
print('   - Kitchen status indicator')
print('   - Active queue metrics')
print('   - Today\'s orders')
print('   - Completion rate')
print('   - Efficiency score')
print('   - Debug information')

print()
print('🐛 IF STILL NOT WORKING:')
print('1. Check browser console for JavaScript errors')
print('2. Check if React is re-rendering the component')
print('3. Verify the debug panel appears')
print('4. Check Network tab for any failed requests')
print('5. Try refreshing the page and clicking again')

print()
print('🚀 MINIMAL COMPONENT SHOULD WORK!')
print('If the minimal component works, the issue is in the original KitchenAnalytics component.')
print('If the minimal component doesn\'t work, the issue is in the Kitchen page state management.')

print()
print('📱 Test URL: http://localhost:8081/kitchen')
