"""
Debug revenue summary date filtering issue
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from datetime import datetime, timedelta

def debug_revenue_summary_dates():
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
                'Authorization': f'Bearer {token}`,
                'Content-Type': 'application/json'
            }
            
            print("🔍 Debugging Revenue Summary Date Filtering:")
            
            # Get all invoices to see their exact timestamps
            print("\n📋 All Invoices with Timestamps:")
            invoices_response = requests.get('http://localhost:8000/api/billing/invoices', headers=headers)
            
            if invoices_response.status_code == 200:
                invoices = invoices_response.json()
                
                for invoice in invoices:
                    created_at = invoice.get('created_at', '')
                    status = invoice.get('status', 'unknown')
                    total = invoice.get('total_amount', 0)
                    
                    print(f"  Invoice: {status} - ₹{total}")
                    print(f"  Created: {created_at}")
                    
                    # Extract date part
                    if created_at:
                        date_part = created_at.split('T')[0]
                        time_part = created_at.split('T')[1][:8] if 'T' in created_at else ''
                        print(f"  Date: {date_part}, Time: {time_part}")
                    print()
            
            # Test revenue summary with different date formats
            invoice_date = '2026-01-29'
            print(f"📊 Testing Revenue Summary for {invoice_date}:")
            
            # Test with different date formats
            test_dates = [
                '2026-01-29',
                '2026-01-29T00:00:00Z',
                '2026-01-29T23:59:59Z'
            ]
            
            for test_date in test_dates:
                print(f"\n  Testing with: {test_date}")
                revenue_response = requests.get(
                    f'http://localhost:8000/api/billing/revenue/summary?start_date={test_date}&end_date={test_date}', 
                    headers=headers
                )
                
                if revenue_response.status_code == 200:
                    data = revenue_response.json()
                    summary = data['summary']
                    print(f"    Revenue: ₹{summary['total_revenue']}")
                    print(f"    Paid Invoices: {summary['paid_invoices']}")
                else:
                    print(f"    Error: {revenue_response.status_code}")
                    
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_revenue_summary_dates()
