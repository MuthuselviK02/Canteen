"""
Test the payment methods fix
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from datetime import datetime, timedelta

def test_payment_methods_fix():
    try:
        login_data = {
            'email': 'superadmin@admin.com',
            'password': 'admin123'
        }
        
        login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data['access_token']
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            print("🧪 Testing Payment Methods Fix:")
            
            # Test the same date range the frontend will use
            endDate = datetime.utcnow().date().isoformat()
            startDate = (datetime.utcnow() - timedelta(days=30)).date().isoformat()
            
            print(f"Using date range: {startDate} to {endDate}")
            
            revenue_response = requests.get(
                f'http://localhost:8000/api/billing/revenue/summary?start_date={startDate}&end_date={endDate}', 
                headers=headers
            )
            
            if revenue_response.status_code == 200:
                revenue_data = revenue_response.json()
                payment_breakdown = revenue_data.get('payment_breakdown', {})
                summary = revenue_data.get('summary', {})
                
                print(f"\n✅ Revenue Summary with Date Range:")
                print(f"  Total Revenue: ₹{summary.get('total_revenue', 0)}")
                print(f"  Paid Invoices: {summary.get('paid_invoices', 0)}")
                print(f"  Pending Invoices: {summary.get('pending_invoices', 0)}")
                
                print(f"\n💳 Payment Methods Breakdown:")
                for method, amount in payment_breakdown.items():
                    if amount > 0:
                        print(f"  {method.capitalize()}: ₹{amount}")
                
                total_payment = sum(payment_breakdown.values())
                print(f"\nTotal Payment Amount: ₹{total_payment}")
                
                if total_payment > 0:
                    print(f"\n🎉 Payment Methods Distribution should now work!")
                    print(f"Expected: Cash payment bar showing ₹{payment_breakdown.get('cash', 0)}")
                else:
                    print(f"\n❌ Still no payment data")
                    
            else:
                print(f"❌ API failed: {revenue_response.status_code}")
                print(revenue_response.text)
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_payment_methods_fix()
