import requests
import json

# Test multiple user credentials
BASE_URL = "http://localhost:8000"

def test_user_credentials(email, password, user_type):
    """Test user login and basic functionality"""
    print(f"\n🔍 Testing {user_type} credentials...")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    
    try:
        # Login
        login_data = {"email": email, "password": password}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if response.status_code != 200:
            print(f"   ❌ Login failed: {response.status_code}")
            return False
            
        token_data = response.json()
        token = token_data.get("access_token")
        
        if not token:
            print("   ❌ No token received")
            return False
            
        print(f"   ✅ Login successful!")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test user info endpoint
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        
        if me_response.status_code == 200:
            user_data = me_response.json()
            print(f"   ✅ User data retrieved:")
            print(f"      Name: {user_data.get('fullname', 'N/A')}")
            print(f"      Email: {user_data.get('email', 'N/A')}")
            print(f"      Role: {user_data.get('role', 'N/A')}")
            print(f"      User ID: {user_data.get('id', 'N/A')}")
            
            # Test menu access (should work for USER role)
            menu_response = requests.get(f"{BASE_URL}/api/menu/", headers=headers)
            if menu_response.status_code == 200:
                menu_items = menu_response.json()
                print(f"   ✅ Menu access: {len(menu_items)} items")
            else:
                print(f"   ❌ Menu access failed: {menu_response.status_code}")
                
            # Test orders access
            orders_response = requests.get(f"{BASE_URL}/api/orders/", headers=headers)
            if orders_response.status_code == 200:
                orders = orders_response.json()
                print(f"   ✅ Orders access: {len(orders)} orders")
            else:
                print(f"   ❌ Orders access failed: {orders_response.status_code}")
                
            return True
        else:
            print(f"   ❌ Failed to get user data: {me_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Test all provided credentials"""
    credentials = [
        {
            "email": "ai@gmail.com",
            "password": "ai12345",
            "type": "AI User"
        },
        {
            "email": "sharan@gmail.com", 
            "password": "sharan@1230",
            "type": "Sharan User"
        }
    ]
    
    print("🧪 USER CREDENTIAL TESTING")
    print("=" * 50)
    
    success_count = 0
    for cred in credentials:
        if test_user_credentials(cred["email"], cred["password"], cred["type"]):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"📊 RESULTS: {success_count}/{len(credentials)} credentials working")
    
    if success_count == len(credentials):
        print("✅ ALL CREDENTIALS ARE WORKING!")
    else:
        print("⚠️  SOME CREDENTIALS FAILED!")

if __name__ == "__main__":
    main()
