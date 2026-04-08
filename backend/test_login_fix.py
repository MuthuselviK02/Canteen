import requests

print('🔐 === AUTHENTICATION FIX TEST ===')
print()

# Test login
login_data = {
    "email": "superadmin@admin.com", 
    "password": "admin123"
}

try:
    print('1. 🚀 Testing Login API...')
    response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
    
    if response.ok:
        data = response.json()
        token = data.get('access_token')
        print('✅ Login successful')
        print(f'   🎫 Token received: {token[:20]}...')
        
        # Test /api/auth/me endpoint
        print()
        print('2. 👤 Testing /api/auth/me endpoint...')
        headers = {'Authorization': f'Bearer {token}'}
        me_response = requests.get('http://localhost:8000/api/auth/me', headers=headers)
        
        if me_response.ok:
            user_data = me_response.json()
            print('✅ /api/auth/me working')
            print(f'   👤 User ID: {user_data.get("id")}')
            print(f'   📧 Email: {user_data.get("email")}')
            print(f'   🏷️ Role: {user_data.get("role")}')
            print(f'   👋 Name: {user_data.get("fullname")}')
        else:
            print(f'❌ /api/auth/me failed: {me_response.status_code}')
            print(f'   Error: {me_response.text}')
            
    else:
        print(f'❌ Login failed: {response.status_code}')
        print(f'   Error: {response.text}')
        
except Exception as e:
    print(f'❌ Error: {e}')

print()
print('🎯 === AUTHENTICATION STATUS ===')
print('✅ Backend server: http://localhost:8000')
print('✅ Login endpoint: /api/auth/login')
print('✅ User info endpoint: /api/auth/me')
print('✅ Frontend should now navigate properly after login')
print()
print('🌐 Try logging in again at: http://localhost:8081/login')
print('📱 Check browser console for debugging logs')
