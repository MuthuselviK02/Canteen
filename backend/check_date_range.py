"""
Check date range issue in payment methods
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from datetime import datetime

def check_date_range():
    try:
        login_data = {
            'email': 'superadmin@admin.com',
            'password': 'admin123'
        }
        
        login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data ['access_token']
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            print("📅 Checking Date Range Issue:")
            
            # Test with explicit date range that includes our invoices
            today = datetime.utcnow()
            start_date = '2026-01-25'  # Before our invoices
            end_date = '2026-02-02'    # After our invoices
            
            print(f"Testing with date range: {start_date} to {end_date}")
            
            revenue_response = requests.get(
                f'http://localhost:8000/api/billing/revenue/summary?start_date={start_date}&end_date={end_date}', 
                headers=headers
            )
            
            if revenue_response.status_code == 200:
                revenue_data = revenue_response.json()
                payment_breakdown = revenue_data.get('payment_breakdown', {})
                
                print(f"Payment Breakdown with date range:")
                print(json.dumps(payment_breakdown, indent=2))
                
                total_payment = sum(payment_breakdown.values())
                print(f"\nTotal Payment Amount: ₹{total_payment}")
                
                if total_payment > 0:
                    print(f"✅ Payment data found with date range!")
                else:
                    print(f"❌ Still no payment data")
                    
            else:
                print(f"❌ API failed: {revenue_response.status_code}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_date_range()
