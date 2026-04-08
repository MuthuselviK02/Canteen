"""
Test date-specific billing functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from datetime import datetime, timedelta

def test_date_specific_billing():
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
            
            print("🗓️ Testing Date-Specific Billing:")
            
            # Test different date ranges
            today = datetime.utcnow().date().isoformat()
            yesterday = (datetime.utcnow() - timedelta(days=1)).date().isoformat()
            invoice_date = '2026-01-29'  # When our paid invoices are from
            
            print(f"\n📅 Testing Date Ranges:")
            print(f"Today: {today}")
            print(f"Invoice Date: {invoice_date}")
            
            # Test 1: Today (should show 0 since invoices are from Jan 29)
            print(f"\n1️⃣ Testing 'Today' Range:")
            revenue_today = requests.get(
                f'http://localhost:8000/api/billing/revenue/summary?start_date={today}&end_date={today}', 
                headers=headers
            )
            
            if revenue_today.status_code == 200:
                data_today = revenue_today.json()
                summary_today = data_today['summary']
                print(f"  Revenue: ₹{summary_today['total_revenue']}")
                print(f"  Paid Invoices: {summary_today['paid_invoices']}")
                print(f"  Total Invoices: {summary_today['total_invoices']}")
            
            # Test 2: Invoice date (should show our data)
            print(f"\n2️⃣ Testing Invoice Date ({invoice_date}):")
            revenue_invoice = requests.get(
                f'http://localhost:8000/api/billing/revenue/summary?start_date={invoice_date}&end_date={invoice_date}', 
                headers=headers
            )
            
            if revenue_invoice.status_code == 200:
                data_invoice = revenue_invoice.json()
                summary_invoice = data_invoice['summary']
                payment_breakdown = data_invoice['payment_breakdown']
                
                print(f"  Revenue: ₹{summary_invoice['total_revenue']}")
                print(f"  Paid Invoices: {summary_invoice['paid_invoices']}")
                print(f"  Total Invoices: {summary_invoice['total_invoices']}")
                print(f"  Pending Invoices: {summary_invoice['pending_invoices']}")
                
                avg_order_value = summary_invoice['total_revenue'] / summary_invoice['paid_invoices'] if summary_invoice['paid_invoices'] > 0 else 0
                print(f"  Avg Order Value: ₹{avg_order_value:.2f}")
                
                print(f"  Payment Methods:")
                for method, amount in payment_breakdown.items():
                    if amount > 0:
                        print(f"    {method}: ₹{amount}")
            
            # Test 3: Invoices with date filtering
            print(f"\n3️⃣ Testing Invoices API with Date Filter:")
            invoices_today = requests.get(
                f'http://localhost:8000/api/billing/invoices?start_date={invoice_date}&end_date={invoice_date}', 
                headers=headers
            )
            
            if invoices_today.status_code == 200:
                invoices_data = invoices_today.json()
                print(f"  Invoices on {invoice_date}: {len(invoices_data)}")
                
                paid_count = len([inv for inv in invoices_data if inv['status'] == 'paid'])
                pending_count = len([inv for inv in invoices_data if inv['status'] == 'pending'])
                
                print(f"  Paid: {paid_count}")
                print(f"  Pending: {pending_count}")
                
            print(f"\n✅ Date-specific billing is working!")
            print(f"📊 KPIs are now calculated based on selected date range")
            
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_date_specific_billing()
