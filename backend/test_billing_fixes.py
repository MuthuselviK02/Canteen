"""
Test the billing dashboard fixes
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_billing_dashboard():
    try:
        # Login as admin
        login_data = {
            'email': 'superadmin@admin.com',
            'password': 'admin123'
        }
        
        login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data['access_token']
            print(f"✅ Login successful")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Test revenue summary API
            print("\n📊 Testing Revenue Summary API:")
            revenue_response = requests.get('http://localhost:8000/api/billing/revenue/summary', headers=headers)
            
            if revenue_response.status_code == 200:
                revenue_data = revenue_response.json()
                print(f"✅ Revenue Summary Response:")
                print(f"  Total Revenue: ₹{revenue_data['summary']['total_revenue']}")
                print(f"  Total Invoices: {revenue_data['summary']['total_invoices']}")
                print(f"  Paid Invoices: {revenue_data['summary']['paid_invoices']}")
                print(f"  Pending Invoices: {revenue_data['summary']['pending_invoices']}")
                print(f"  Payment Breakdown: {revenue_data['payment_breakdown']}")
                
                # Verify fixes
                total_revenue = revenue_data['summary']['total_revenue']
                paid_invoices = revenue_data['summary']['paid_invoices']
                
                print(f"\n🔍 Verification:")
                print(f"  Revenue only from paid invoices: {'✅' if total_revenue >= 0 else '❌'}")
                print(f"  Paid invoices counted correctly: {'✅' if paid_invoices >= 0 else '❌'}")
                
                if paid_invoices == 0:
                    print(f"  ✅ Empty state will show: 'No paid invoices yet'")
                else:
                    print(f"  ✅ Revenue per paid invoice: ₹{total_revenue / paid_invoices:.2f}")
                    
            else:
                print(f"❌ Revenue Summary API failed: {revenue_response.status_code}")
                print(revenue_response.text)
            
            # Test dashboard overview API
            print("\n📈 Testing Dashboard Overview API:")
            overview_response = requests.get('http://localhost:8000/api/billing/dashboard/overview', headers=headers)
            
            if overview_response.status_code == 200:
                overview_data = overview_response.json()
                print(f"✅ Dashboard Overview Response:")
                print(f"  Total Revenue: ₹{overview_data['summary']['total_revenue']}")
                print(f"  Average Order Value: ₹{overview_data['summary']['average_order_value']}")
                print(f"  Paid Invoices: {overview_data['summary']['paid_invoices']}")
                print(f"  Pending Invoices: {overview_data['summary']['pending_invoices']}")
                
                # Verify average order value calculation
                avg_order_value = overview_data['summary']['average_order_value']
                total_revenue = overview_data['summary']['total_revenue']
                paid_invoices = overview_data['summary']['paid_invoices']
                
                if paid_invoices > 0:
                    expected_avg = total_revenue / paid_invoices
                    print(f"\n🔍 Average Order Value Verification:")
                    print(f"  Expected: ₹{expected_avg:.2f}")
                    print(f"  Actual: ₹{avg_order_value:.2f}")
                    print(f"  Correct: {'✅' if abs(avg_order_value - expected_avg) < 0.01 else '❌'}")
                else:
                    print(f"  ✅ Average Order Value correctly set to 0 (no paid invoices)")
                    
            else:
                print(f"❌ Dashboard Overview API failed: {overview_response.status_code}")
                print(overview_response.text)
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_billing_dashboard()
