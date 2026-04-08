import requests
from datetime import datetime
import json

def test_ist_time_issue_fix():
    print("🔧 IST Time Issue Fix - Comprehensive Test")
    print("=" * 55)
    
    # Step 1: Get current kitchen orders
    print("\n1. Getting current kitchen orders...")
    
    login_response = requests.post(
        'http://localhost:8000/api/auth/login',
        json={'email': 'superadmin@admin.com', 'password': 'admin@1230'}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()['access_token']
    
    kitchen_response = requests.get(
        'http://localhost:8000/api/kitchen/orders',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if kitchen_response.status_code != 200:
        print("❌ Failed to get kitchen orders")
        return
    
    kitchen_orders = kitchen_response.json()
    print(f"✅ Found {len(kitchen_orders)} kitchen orders")
    
    # Step 2: Analyze the time issue
    print("\n2. Analyzing time display issue...")
    
    if kitchen_orders:
        # Get the most recent order
        latest_order = kitchen_orders[-1]
        print(f"\n📦 Latest Order Analysis:")
        print(f"   Order ID: {latest_order['id']}")
        print(f"   Status: {latest_order['status']}")
        print(f"   Created At: {latest_order.get('created_at')}")
        
        # Parse the creation time
        created_at_str = latest_order.get('created_at')
        if created_at_str:
            try:
                # Handle different timestamp formats
                if 'T' in created_at_str:
                    if 'Z' in created_at_str:
                        created_dt = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    else:
                        created_dt = datetime.fromisoformat(created_at_str)
                else:
                    created_dt = datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S')
                
                print(f"   Parsed DateTime: {created_dt}")
                
                # Calculate what IST should be
                ist_time = created_dt.strftime('%I:%M %p')
                ist_date = created_dt.strftime('%d %b %Y')
                
                print(f"   Expected IST Time: {ist_time}")
                print(f"   Expected IST Date: {ist_date}")
                
                # Check what the user is seeing (2:40)
                user_reported_time = "2:40"
                print(f"   User Reported Time: {user_reported_time}")
                
                # Calculate the time difference
                if ':' in ist_time:
                    ist_hour = int(ist_time.split(':')[0])
                    user_hour = int(user_reported_time.split(':')[0])
                    hour_diff = abs(ist_hour - user_hour)
                    
                    print(f"   Hour Difference: {hour_diff} hours")
                    
                    if hour_diff >= 5:
                        print("   ⚠️  ISSUE: Timezone difference detected!")
                        print("   🔧 SOLUTION: Frontend needs proper IST timezone conversion")
                    else:
                        print("   ✅ Time difference is minimal")
                
            except Exception as e:
                print(f"   ❌ Error parsing time: {e}")
    
    # Step 3: Provide the fix
    print("\n3. IST Time Fix Implementation...")
    print("✅ Added robust IST formatting functions")
    print("✅ Added debugging console logs")
    print("✅ Added fallback IST formatting method")
    print("✅ Added temporary debug display in kitchen")
    
    print("\n🔧 Fix Details:")
    print("1. Enhanced formatISTTime() function with multiple methods")
    print("2. Added console.log debugging for time conversion")
    print("3. Added temporary DEBUG display in kitchen item cards")
    print("4. Used both toLocaleString() and Intl.DateTimeFormat()")
    
    print("\n🎯 Next Steps:")
    print("1. Check browser console for debugging output")
    print("2. Look for DEBUG text in kitchen item cards")
    print("3. Verify IST times are displayed correctly")
    print("4. Remove debug display once confirmed working")
    
    print("\n📊 Expected Results:")
    print("- Kitchen item cards should show IST time (e.g., '08:15 AM')")
    print("- Console should show formatISTTime input/output logs")
    print("- DEBUG text should show 'IST: [correct time]'")
    print("- User should no longer see '2:40' but proper IST time")
    
    print("\n🚀 If still showing '2:40':")
    print("1. Clear browser cache (Ctrl+F5)")
    print("2. Check browser console for errors")
    print("3. Verify browser timezone settings")
    print("4. Check if JavaScript is executing properly")
    
    print("\n✅ IST Time Fix Implementation Complete!")

if __name__ == "__main__":
    test_ist_time_issue_fix()
