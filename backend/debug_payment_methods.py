"""
Debug payment methods distribution issue
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def debug_payment_methods():
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
            
            print("🔍 Debugging Payment Methods Distribution:")
            
            # Check all invoices with their payment methods
            print("\n📋 Checking All Invoices:")
            invoices_response = requests.get('http://localhost:8000/api/billing/invoices', headers=headers)
            
            if invoices_response.status_code == 200:
                invoices = invoices_response.json()
                
                paid_invoices = []
                for invoice in invoices:
                    status = invoice.get('status', 'unknown')
                    payment_method = invoice.get('payment_method', 'NOT_SET')
                    total = invoice.get('total_amount', 0)
                    
                    print(f"  Invoice #{invoice['id'][:8]}...: {status} - ₹{total} - Payment: {payment_method}")
                    
                    if status == 'paid':
                        paid_invoices.append({
                            'id': invoice['id'],
                            'payment_method': payment_method,
                            'amount': total
                        })
                
                print(f"\n✅ Paid Invoices: {len(paid_invoices)}")
                payment_methods = {}
                for inv in paid_invoices:
                    method = inv['payment_method']
                    if method not in payment_methods:
                        payment_methods[method] = 0
                    payment_methods[method] += inv['amount']
                
                print(f"Payment Method Breakdown:")
                for method, amount in payment_methods.items():
                    print(f"  {method}: ₹{amount}")
            
            # Check revenue summary API
            print("\n📊 Checking Revenue Summary API:")
            revenue_response = requests.get('http://localhost:8000/api/billing/revenue/summary', headers=headers)
            
            if revenue_response.status_code == 200:
                revenue_data = revenue_response.json()
                payment_breakdown = revenue_data.get('payment_breakdown', {})
                
                print(f"Payment Breakdown from API:")
                print(json.dumps(payment_breakdown, indent=2))
                
                total_payment = sum(payment_breakdown.values())
                print(f"\nTotal Payment Amount: ₹{total_payment}")
                
                if total_payment > 0:
                    print(f"✅ Payment data should be visible!")
                else:
                    print(f"❌ No payment data - all payment methods are empty")
                    
            else:
                print(f"❌ Revenue Summary API failed: {revenue_response.status_code}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_payment_methods()
