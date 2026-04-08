import requests
import json

print('🔍 === AUTHENTICATION DEBUG TEST ===')
print()

# Test 1: Health check
print('1. 🏥 Testing Backend Health...')
try:
    response = requests.get('http://localhost:8000/health', timeout=5)
    if response.ok:
        print('✅ Backend is running')
    else:
        print('❌ Backend not responding')
        exit()
except Exception as e:
    print(f'❌ Backend connection error: {e}')
    exit()

print()

# Test 2: Login endpoint
print('2. 🔐 Testing Login Endpoint...')
login_data = {
    "email": "superadmin@admin.com", 
    "password": "admin123"
}

try:
    response = requests.post('http://localhost:8000/api/auth/login', json=login_data, timeout=5)
    print(f'   Status Code: {response.status_code}')
    
    if response.ok:
        data = response.json()
        token = data.get('access_token')
        print('✅ Login successful')
        print(f'   Token: {token[:30]}...' if token else '❌ No token received')
        
        # Test 3: /api/auth/me endpoint
        print()
        print('3. 👤 Testing /api/auth/me Endpoint...')
        headers = {'Authorization': f'Bearer {token}'}
        
        me_response = requests.get('http://localhost:8000/api/auth/me', headers=headers, timeout=5)
        print(f'   Status Code: {me_response.status_code}')
        
        if me_response.ok:
            user_data = me_response.json()
            print('✅ /api/auth/me working')
            print(f'   User ID: {user_data.get("id")}')
            print(f'   Email: {user_data.get("email")}')
            print(f'   Role: {user_data.get("role")}')
            print(f'   Name: {user_data.get("fullname")}')
        else:
            print('❌ /api/auth/me failed')
            print(f'   Response: {me_response.text}')
            
    else:
        print('❌ Login failed')
        print(f'   Response: {response.text}')
        
except Exception as e:
    print(f'❌ Error: {e}')

print()
print('🎯 === DEBUGGING TIPS ===')
print('1. Check browser console (F12) for JavaScript errors')
print('2. Check Network tab for failed API calls')
print('3. Verify backend is running on port 8000')
print('4. Try clearing browser cache and localStorage')
print()
print('🌐 If backend is working, the issue might be:')
print('   - Frontend JavaScript error')
print('   - CORS issue')
print('   - Browser cache issue')
print('   - Network connectivity issue')
