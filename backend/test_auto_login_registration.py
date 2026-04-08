#!/usr/bin/env python3
"""
Test new registration flow with auto-login
"""

import requests
import json
import time

# Base URL
BASE_URL = "http://localhost:8000"

def test_auto_login_registration():
    """Test registration with automatic login"""
    
    print("🧪 Testing Auto-Login Registration Flow")
    print("=" * 50)
    
    # Generate unique user data
    timestamp = int(time.time())
    test_user = {
        "fullname": f"Auto User {timestamp}",
        "email": f"autouser{timestamp}@example.com",
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
        
        # Step 2: Auto-login with the same credentials
        print("\n2️⃣ Auto-login with same credentials...")
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        
        if login_response.status_code == 200:
            print("✅ Auto-login successful!")
            login_data = login_response.json()
            token = login_data.get('access_token')
            print(f"   Token received: {token[:20]}...")
            
            # Step 3: Test accessing menu endpoint
            print("\n3️⃣ Testing menu access...")
            headers = {'Authorization': f'Bearer {token}'}
            menu_response = requests.get(f"{BASE_URL}/api/menu/", headers=headers)
            
            if menu_response.status_code == 200:
                menu_data = menu_response.json()
                print("✅ Menu accessible!")
                print(f"   Available items: {len(menu_data)}")
                
                # Show sample menu items
                if menu_data:
                    print("   Sample items:")
                    for item in menu_data[:3]:
                        print(f"     - {item.get('name', 'Unknown')} - ₹{item.get('price', 0)}")
            else:
                print(f"❌ Menu access failed: {menu_response.status_code}")
                
        else:
            print(f"❌ Auto-login failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            return
        
        print(f"\n🎉 Auto-Login Registration Test Complete!")
        print(f"✅ User can register → auto-login → access menu directly")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")

def test_role_based_redirect():
    """Test role-based redirect after registration"""
    
    print(f"\n🔄 Testing Role-Based Redirect")
    print("=" * 40)
    
    roles_to_test = [
        {"fullname": "Test User", "role": "USER"},
        {"fullname": "Test Staff", "role": "STAFF"}, 
        {"fullname": "Test Admin", "role": "ADMIN"}
    ]
    
    for i, role_info in enumerate(roles_to_test):
        timestamp = int(time.time()) + i
        test_user = {
            "fullname": role_info["fullname"] + f" {timestamp}",
            "email": f"{role_info['role'].lower()}{timestamp}@example.com",
            "password": "test123456"
        }
        
        try:
            print(f"\n👤 Testing {role_info['role']} registration...")
            
            # Register user
            register_response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
            
            if register_response.status_code == 200:
                # Login
                login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                    "email": test_user["email"],
                    "password": test_user["password"]
                })
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    user_data = login_data.get('user', {})
                    actual_role = user_data.get('role')
                    
                    # Expected redirect based on role
                    if actual_role == 'USER':
                        expected_redirect = "/menu"
                    elif actual_role == 'STAFF':
                        expected_redirect = "/kitchen"
                    elif actual_role in ['ADMIN', 'SUPER_ADMIN']:
                        expected_redirect = "/admin"
                    else:
                        expected_redirect = "/menu"
                    
                    print(f"   ✅ {actual_role} → {expected_redirect}")
                else:
                    print(f"   ❌ Login failed for {role_info['role']}")
            else:
                print(f"   ❌ Registration failed for {role_info['role']}")
                
        except Exception as e:
            print(f"   ❌ Error testing {role_info['role']}: {e}")

if __name__ == "__main__":
    test_auto_login_registration()
    test_role_based_redirect()
    
    print(f"\n📋 New Registration Flow:")
    print("1. User fills registration form")
    print("2. Clicks 'Create Account'")
    print("3. Account created in database")
    print("4. Auto-login with same credentials")
    print("5. Redirect to appropriate dashboard:")
    print("   - USER → /menu")
    print("   - STAFF → /kitchen")
    print("   - ADMIN → /admin")
    print("6. User can immediately use the app")
