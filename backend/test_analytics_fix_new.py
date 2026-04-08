"""
Test the analytics fix endpoint
"""
import requests

def test_analytics_fix():
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
        
        # Test analytics fix endpoint
        print("\n📊 Testing analytics fix endpoint...")
        response = requests.get('http://localhost:8000/api/analytics-dashboard-fix', headers=headers)
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ Analytics fix data received')
            
            # Check key metrics
            kpis = data.get('kpis', {})
            print(f'\n📈 Key Performance Indicators:')
            print(f'  Revenue: ₹{kpis.get("revenue", 0)}')
            print(f'  Orders: {kpis.get("orders", 0)}')
            print(f'  Avg Order Value: ₹{kpis.get("avg_order_value", 0)}')
            print(f'  Customers: {kpis.get("customers", 0)}')
            print(f'  Revenue Growth: {kpis.get("revenue_growth", 0)}%')
            print(f'  Orders Growth: {kpis.get("orders_growth", 0)}%')
            
            # Check time slots
            time_slots = data.get('time_slot_analysis', {})
            slots = time_slots.get('slots', {})
            print(f'\n⏰ Time Slot Analysis:')
            for slot_name, slot_data in slots.items():
                revenue = slot_data.get('revenue', 0)
                orders = slot_data.get('orders', 0)
                print(f'  {slot_name}: ₹{revenue} ({orders} orders)')
            
            # Check top items
            top_items = data.get('item_performance', {}).get('top_selling', [])
            print(f'\n🍽️ Top Selling Items:')
            for item in top_items[:5]:
                print(f'  {item.get("name")}: {item.get("orders")} orders • ₹{item.get("revenue")}')
            
        else:
            print(f'❌ Analytics fix endpoint failed: {response.status_code}')
            print(f'Error details: {response.text}')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    print("🧪 Testing Analytics Fix Endpoint")
    print("=" * 50)
    test_analytics_fix()
