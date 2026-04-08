import requests
import time
import json

# Configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/auth/login"
RATE_LIMIT_REQUESTS = 100  # From your .env file
RATE_LIMIT_WINDOW = 60      # 60 seconds

def test_rate_limiting():
    print(f"🧪 Testing Rate Limiting for {ENDPOINT}")
    print(f"📊 Rate Limit: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds")
    print("=" * 60)
    
    # Test data for login
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    success_count = 0
    rate_limited_count = 0
    other_errors = 0
    
    print("🚀 Sending rapid requests...")
    
    # Send requests rapidly to trigger rate limiting
    for i in range(1, RATE_LIMIT_REQUESTS + 20):  # Send 20 extra requests
        try:
            response = requests.post(
                f"{BASE_URL}{ENDPOINT}",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 429:
                rate_limited_count += 1
                print(f"⏱️  Request {i}: Rate Limited (429) - {response.json().get('detail', 'No detail')}")
            elif response.status_code in [200, 401]:
                success_count += 1
                print(f"✅ Request {i}: Success ({response.status_code})")
            else:
                other_errors += 1
                print(f"❌ Request {i}: Other Error ({response.status_code}) - {response.text}")
                
        except requests.exceptions.RequestException as e:
            other_errors += 1
            print(f"🔌 Request {i}: Connection Error - {str(e)}")
    
    print("\n" + "=" * 60)
    print("📈 RESULTS:")
    print(f"✅ Successful requests: {success_count}")
    print(f"⏱️  Rate limited requests: {rate_limited_count}")
    print(f"❌ Other errors: {other_errors}")
    print(f"📊 Total requests sent: {success_count + rate_limited_count + other_errors}")
    
    if rate_limited_count > 0:
        print("\n🎉 Rate Limiting is WORKING! 🎉")
        print(f"✅ Requests were properly rate limited after reaching the threshold")
    else:
        print("\n⚠️  Rate Limiting might NOT be working")
        print("❌ No rate limiting responses were received")
    
    print("\n🔍 Testing rate limit recovery...")
    print("⏳ Waiting 5 seconds...")
    time.sleep(5)
    
    # Test one more request after waiting
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 429:
            print("⏱️  Still rate limited after 5 seconds")
        else:
            print(f"✅ Request succeeded after waiting: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"🔌 Connection error during recovery test: {str(e)}")

def test_different_endpoints():
    print("\n" + "=" * 60)
    print("🧪 Testing Rate Limiting on Different Endpoints")
    print("=" * 60)
    
    endpoints = [
        "/api/menu/",
        "/api/auth/register",
    ]
    
    for endpoint in endpoints:
        print(f"\n📍 Testing: {endpoint}")
        
        try:
            if endpoint == "/api/auth/register":
                data = {
                    "fullname": "Test User",
                    "email": "test@example.com",
                    "password": "password123"
                }
                response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=5)
            else:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 429:
                print("⏱️  Rate limited!")
            else:
                print("✅ No rate limiting on this request")
                
        except requests.exceptions.RequestException as e:
            print(f"🔌 Error: {str(e)}")

if __name__ == "__main__":
    test_rate_limiting()
    test_different_endpoints()
