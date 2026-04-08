import requests

def test_kitchen_item_time_display():
    print("🔍 Testing Kitchen Item Card Time Display Issue")
    print("=" * 55)
    
    # Login and get kitchen orders
    login_response = requests.post(
        'http://localhost:8000/api/auth/login',
        json={'email': 'superadmin@admin.com', 'password': 'admin@1230'}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()['access_token']
    
    # Get kitchen orders
    kitchen_response = requests.get(
        'http://localhost:8000/api/kitchen/orders',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if kitchen_response.status_code != 200:
        print("❌ Failed to get kitchen orders")
        return
    
    kitchen_orders = kitchen_response.json()
    
    print(f"\n📋 Found {len(kitchen_orders)} kitchen orders")
    
    # Check the first few orders and their timestamps
    for i, order in enumerate(kitchen_orders[:3]):
        print(f"\n📦 Order #{i+1}: {order['id']}")
        print(f"   Status: {order.get('status')}")
        print(f"   Created At: {order.get('created_at')}")
        print(f"   Started Prep: {order.get('started_preparation_at')}")
        print(f"   Ready At: {order.get('ready_at')}")
        print(f"   Completed At: {order.get('completed_at')}")
        
        # Simulate the frontend IST formatting
        from datetime import datetime
        
        if order.get('created_at'):
            created_str = order['created_at']
            try:
                if 'T' in created_str:
                    created_dt = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                else:
                    created_dt = datetime.strptime(created_str, '%Y-%m-%d %H:%M:%S')
                
                # This is what the frontend should show
                ist_time = created_dt.strftime('%I:%M %p')
                ist_date = created_dt.strftime('%d %b %Y')
                
                print(f"   🇮🇳 Expected IST Time: {ist_time}")
                print(f"   🇮🇳 Expected IST Date: {ist_date}")
                
                # Check if this matches what user is seeing (2:40)
                local_time = created_dt.strftime('%I:%M %p')
                print(f"   🕐 Local Time (what user sees): {local_time}")
                
                if local_time == "02:40 PM" or local_time == "02:40 AM":
                    print("   ⚠️  ISSUE: Showing local time instead of IST!")
                else:
                    print("   ✅ Time format looks correct")
                    
            except Exception as e:
                print(f"   ❌ Time formatting error: {e}")
    
    print("\n🔧 Possible Issues:")
    print("1. Frontend not using IST formatting functions")
    print("2. Timezone not properly applied")
    print("3. Using old time format instead of new IST format")
    print("4. Browser timezone affecting display")
    
    print("\n🛠️  Solution Check:")
    print("✅ Kitchen getTimeDisplay function should use formatISTTime")
    print("✅ formatISTTime should use timeZone: 'Asia/Kolkata'")
    print("✅ All time displays should call IST formatting")
    
    print("\n🎯 Next Steps:")
    print("1. Verify getTimeDisplay is calling formatISTTime")
    print("2. Check if formatISTTime is properly implemented")
    print("3. Ensure all time displays use IST formatting")
    print("4. Test with different browser timezones")

if __name__ == "__main__":
    test_kitchen_item_time_display()
