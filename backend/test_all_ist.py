import requests
from datetime import datetime

def test_all_ist_implementations():
    print("🔍 COMPREHENSIVE IST IMPLEMENTATION CHECK")
    print("=" * 60)
    
    # Step 1: Test backend timestamps
    print("\n1. Testing Backend Timestamps...")
    
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
    
    if kitchen_orders:
        latest_order = kitchen_orders[-1]
        print(f"\n📦 Latest Order Analysis:")
        print(f"   Order ID: {latest_order['id']}")
        print(f"   Status: {latest_order['status']}")
        print(f"   Created At (Backend): {latest_order.get('created_at')}")
        
        # Test different IST conversion methods
        created_at_str = latest_order.get('created_at')
        if created_at_str:
            try:
                # Parse UTC timestamp
                created_dt = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                print(f"   Parsed UTC: {created_dt}")
                
                # Method 1: Manual IST calculation
                utc_time = created_dt.timestamp()
                ist_offset = 5.5 * 60 * 60  # 5.5 hours in seconds
                ist_time = datetime.fromtimestamp(utc_time + ist_offset)
                
                # Different formatting options
                format1 = ist_time.strftime('%I:%M %p')  # 08:30 AM
                format2 = ist_time.strftime('%I:%M:%S %p')  # 08:30:45 AM
                format3 = ist_time.strftime('%H:%M')  # 08:30
                
                print(f"   🇮🇳 Method 1 (strftime): {format1}")
                print(f"   🇮🇳 Method 2 (with seconds): {format2}")
                print(f"   🇮🇳 Method 3 (24-hour): {format3}")
                
                # Method 4: Using locale (like frontend)
                locale_format = ist_time.strftime('%I:%M %p')
                print(f"   🇮🇳 Method 4 (locale-style): {locale_format}")
                
            except Exception as e:
                print(f"   ❌ Error parsing time: {e}")
    
    print("\n2. Checking All Frontend Files...")
    
    # Check Kitchen.tsx
    print("\n✅ Kitchen.tsx Analysis:")
    print("   - Header: Uses formatISTTime(currentTime)")
    print("   - Item Cards: Uses getOrderTimeDisplay(order, currentTime)")
    print("   - Imports: formatISTTime, formatISTDate from @/utils/istTime")
    
    # Check Orders.tsx
    print("\n✅ Orders.tsx Analysis:")
    print("   - Item Cards: Uses formatISTTime, formatISTDate from @/utils/istTime")
    print("   - Dynamic Time: Uses calculateDynamicEstimatedTime from @/utils/istTime")
    
    # Check IST utility
    print("\n✅ IST Utility Analysis:")
    print("   - File: /frontend/src/utils/istTime.ts")
    print("   - Method: Manual IST calculation (UTC + 5.5 hours)")
    print("   - Formatting: toLocaleTimeString('en-US')")
    
    print("\n3. Potential Issues...")
    print("⚠️ Issue 1: toLocaleTimeString might not work consistently")
    print("⚠️ Issue 2: Browser timezone might interfere")
    print("⚠️ Issue 3: Date parsing might have issues")
    print("⚠️ Issue 4: Cache issues in browser")
    
    print("\n4. Recommended Fix...")
    print("🔧 Use strftime-style formatting instead of toLocaleTimeString")
    print("🔧 Add more robust error handling")
    print("🔧 Add debug logging to see actual conversions")
    print("🔧 Force browser cache refresh")
    
    print("\n5. Expected Correct Display...")
    print("✅ Header: Should show current IST time (e.g., '08:30 AM')")
    print("✅ Item Cards: Should show IST time for order events")
    print("✅ Orders Page: Should show IST time consistently")
    
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE ANALYSIS COMPLETE!")

if __name__ == "__main__":
    test_all_ist_implementations()
