"""
Test the simple analytics endpoint
"""
import requests

def test_simple_analytics():
    try:
        # Login with user credentials
        login_data = {
            'email': 'sharan@gmail.com',
            'password': 'sharan@1230'
        }
        
        print("🔐 Logging in...")
        login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f'❌ Login failed: {login_response.status_code}')
            return
        
        token = login_response.json()['access_token']
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        print("✅ Login successful")
        
        # Test simple analytics endpoint
        print("\n📊 Testing simple analytics endpoint...")
        response = requests.get('http://localhost:8000/api/simple-analytics/dashboard-summary', headers=headers)
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ Simple analytics data received')
            
            # Check key metrics
            kpis = data.get('kpis', {})
            print(f'\n📈 Key Performance Indicators:')
            print(f'  Revenue: ₹{kpis.get("revenue", 0)}')
            print(f'  Orders: {kpis.get("orders", 0)}')
            print(f'  Avg Order Value: ₹{kpis.get("avg_order_value", 0)}')
            print(f'  Customers: {kpis.get("customers", 0)}')
            print(f'  Revenue Growth: {kpis.get("revenue_growth", 0)}%')
            print(f'  Orders Growth: {kpis.get("orders_growth", 0)}%')
            
        else:
            print(f'❌ Simple analytics endpoint failed: {response.status_code}')
            print(f'Error details: {response.text}')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    print("🧪 Testing Simple Analytics Endpoint")
    print("=" * 50)
    test_simple_analytics()
