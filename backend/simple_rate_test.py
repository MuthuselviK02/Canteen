import requests
import time

# Configuration
BASE_URL = "http://localhost:8000"

def test_auth_rate_limiting():
    print("🧪 Testing Auth Rate Limiting (5 requests per minute)")
    print("=" * 60)
    
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    print("🚀 Sending 7 rapid requests to /api/auth/login (limit is 5/minute)...")
    
    for i in range(1, 8):  # Send 7 requests (limit is 5)
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 429:
                print(f"⏱️  Request {i}: RATE LIMITED (429)")
                print(f"   Response: {response.json()}")
            elif response.status_code == 401:
                print(f"✅ Request {i}: Success (401 - Wrong password)")
            else:
                print(f"❌ Request {i}: Other ({response.status_code})")
                
        except Exception as e:
            print(f"🔌 Request {i}: Error - {str(e)}")
    
    print("\n📊 Test completed!")
    print("If you saw 'RATE LIMITED' messages, rate limiting is working!")

def test_manual_curl():
    print("\n" + "=" * 60)
    print("🔧 Manual Testing with curl Commands")
    print("=" * 60)
    
    print("Run these commands in your terminal:")
    print("\n1. Test 6 rapid requests (limit is 5/minute):")
    
    for i in range(1, 7):
        print(f'curl -X POST "{BASE_URL}/api/auth/login" \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f'  -d \'{{"email": "test@example.com", "password": "wrongpassword"}}\'')
        print()
    
    print("2. Check response headers:")
    print('curl -I -X POST "http://localhost:8000/api/auth/login" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"email": "test@example.com", "password": "wrongpassword"}\'')
    
    print("\n3. Look for these headers in rate limited responses:")
    print("   - X-RateLimit-Limit: 5")
    print("   - X-RateLimit-Remaining: 0") 
    print("   - X-RateLimit-Reset: <timestamp>")
    print("   - Retry-After: <seconds>")

if __name__ == "__main__":
    test_auth_rate_limiting()
    test_manual_curl()
