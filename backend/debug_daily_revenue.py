"""
Debug why daily revenue shows zeros despite having paid invoices
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from datetime import datetime, timedelta

def debug_daily_revenue():
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
                'Authorization': f'Bearer {token}`,
                'Content-Type': 'application/json'
            }
            
            # First, check all invoices to see their dates and status
            print("\n📋 Checking All Invoices:")
            invoices_response = requests.get('http://localhost:8000/api/billing/invoices', headers=headers)
            
            if invoices_response.status_code == 200:
                invoices = invoices_response.json()
                print(f"Total invoices: {len(invoices)}")
                
                paid_invoices = []
                for invoice in invoices:
                    created_date = invoice.get('created_at', '')[:10]  # Get date part
                    status = invoice.get('status', 'unknown')
                    total = invoice.get('total_amount', 0)
                    
                    print(f"  Invoice #{invoice['id']}: {status} - ₹{total} - Created: {created_date}")
                    
                    if status == 'paid':
                        paid_invoices.append({
                            'id': invoice['id'],
                            'date': created_date,
                            'amount': total
                        })
                
                print(f"\n✅ Paid Invoices: {len(paid_invoices)}")
                for inv in paid_invoices:
                    print(f"  Invoice #{inv['id']}: ₹{inv['amount']} on {inv['date']}")
            
            # Now check daily revenue API
            print("\n📈 Checking Daily Revenue API:")
            daily_response = requests.get('http://localhost:8000/api/billing/revenue/daily?days=7', headers=headers)
            
            if daily_response.status_code == 200:
                daily_data = daily_response.json()
                daily_revenue = daily_data.get('daily_revenue', [])
                
                print(f"Daily revenue data ({len(daily_revenue)} days):")
                for day in daily_revenue:
                    print(f"  {day['date']}: ₹{day['revenue']} ({day['orders']} orders)")
                
                # Check if paid invoice dates match the daily revenue dates
                print(f"\n🔍 Date Matching Analysis:")
                paid_dates = set(inv['date'] for inv in paid_invoices)
                revenue_dates = set(day['date'] for day in daily_revenue)
                
                print(f"Paid invoice dates: {paid_dates}")
                print(f"Revenue query dates: {revenue_dates}")
                
                # Check if any paid invoices are outside the 7-day range
                today = datetime.utcnow().date()
                seven_days_ago = today - timedelta(days=7)
                
                print(f"\n📅 Date Range Analysis:")
                print(f"Today: {today}")
                print(f"7 days ago: {seven_days_ago}")
                
                for inv in paid_invoices:
                    inv_date = datetime.strptime(inv['date'], '%Y-%m-%d').date()
                    in_range = seven_days_ago <= inv_date <= today
                    print(f"  Invoice #{inv['id']} ({inv['date']}): {'✅ in range' if in_range else '❌ out of range'}")
                    
            else:
                print(f"❌ Daily Revenue API failed: {daily_response.status_code}")
                print(daily_response.text)
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_daily_revenue()
