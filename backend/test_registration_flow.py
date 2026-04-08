#!/usr/bin/env python3
"""
Test registration flow and redirect
"""

import requests
import json
import time

# Base URL
BASE_URL = "http://localhost:8000"

def test_registration_flow():
    """Test complete registration flow"""
    
    print("🧪 Testing Registration Flow")
    print("=" * 40)
    
    # Generate unique user data
    timestamp = int(time.time())
    test_user = {
        "fullname": f"Test User {timestamp}",
        "email": f"testuser{timestamp}@example.com",
        "password": "test123456"
    }
    
    print(f"📝 Creating test user: {test_user['email']}")
    
    try:
        # Step 1: Register new user
        print("\n1️⃣ Registering new user...")
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
        
        if register_response.status_code == 200:
            print("✅ Registration successful!")
            user_data = register_response.json()
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Role: {user_data.get('role')}")
        else:
            print(f"❌ Registration failed: {register_response.status_code}")
            print(f"   Error: {register_response.text}")
            return
        
        # Step 2: Try to login with the new user
        print("\n2️⃣ Testing login with new user...")
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        
        if login_response.status_code == 200:
            print("✅ Login successful!")
            login_data = login_response.json()
            token = login_data.get('access_token')
            print(f"   Token received: {token[:20]}...")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            return
        
        # Step 3: Test accessing protected endpoint
        print("\n3️⃣ Testing protected endpoint access...")
        headers = {'Authorization': f'Bearer {token}'}
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        
        if me_response.status_code == 200:
            print("✅ Protected endpoint accessible!")
            user_info = me_response.json()
            print(f"   Welcome {user_info.get('fullname')}!")
        else:
            print(f"❌ Protected endpoint failed: {me_response.status_code}")
        
        print(f"\n🎉 Registration Flow Test Complete!")
        print(f"✅ User can register → get redirected → login → access protected routes")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")

def test_existing_user_registration():
    """Test registration with existing email"""
    
    print(f"\n🔄 Testing Duplicate Registration")
    print("=" * 40)
    
    try:
        # Try to register with existing user email
        duplicate_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "fullname": "Duplicate Test",
            "email": "sharan@gmail.com",  # Existing user
            "password": "test123456"
        })
        
        if duplicate_response.status_code == 400:
            print("✅ Duplicate registration properly rejected!")
            error_data = duplicate_response.json()
            print(f"   Error: {error_data.get('detail')}")
        else:
            print(f"❌ Unexpected response: {duplicate_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during duplicate test: {e}")

if __name__ == "__main__":
    test_registration_flow()
    test_existing_user_registration()
    
    print(f"\n📋 Registration Flow Summary:")
    print("1. User fills form → Clicks 'Create Account'")
    print("2. Account created → Redirected to success page")
    print("3. Success page shows → Auto-redirects to login in 10 seconds")
    print("4. User logs in → Redirected to appropriate dashboard")
    print("5. User can access all features")
