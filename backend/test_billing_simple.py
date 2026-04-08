import requests

# Test billing API
print("🧾 Testing Basic Billing System...")

try:
    # Test health check
    response = requests.get("http://localhost:8000/health")
    if response.ok:
        print("✅ Backend server is running")
    else:
        print("❌ Backend server not responding")
        exit()
    
    # Test login
    login_data = {"email": "superadmin@admin.com", "password": "admin123"}
    login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    
    if login_response.ok:
        token = login_response.json().get("access_token")
        print("✅ Authentication successful")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Test billing settings
        settings_response = requests.get("http://localhost:8000/api/billing/settings", headers=headers)
        if settings_response.ok:
            settings = settings_response.json()
            print("✅ Billing settings working")
            print(f"   Currency: {settings.get('currency', 'INR')}")
            print(f"   Tax Rate: {settings.get('tax_rate', 18)}%")
        else:
            print("❌ Billing settings failed")
        
        # Test invoice creation
        invoice_data = {
            "customer_id": "1",
            "items": [{"name": "Test Item", "price": 100.00, "quantity": 1}],
            "notes": "Test invoice"
        }
        
        invoice_response = requests.post("http://localhost:8000/api/billing/invoices", json=invoice_data, headers=headers)
        if invoice_response.ok:
            invoice = invoice_response.json()
            print("✅ Invoice creation working")
            print(f"   Invoice Number: {invoice.get('invoice_number')}")
            print(f"   Total Amount: ₹{invoice.get('total_amount', 0):.2f}")
        else:
            print("❌ Invoice creation failed")
            print(f"   Error: {invoice_response.text}")
        
        # Test revenue summary
        revenue_response = requests.get("http://localhost:8000/api/billing/revenue/summary", headers=headers)
        if revenue_response.ok:
            revenue = revenue_response.json()
            print("✅ Revenue summary working")
            print(f"   Total Revenue: ₹{revenue.get('summary', {}).get('total_revenue', 0):.2f}")
            print(f"   Total Invoices: {revenue.get('summary', {}).get('total_invoices', 0)}")
        else:
            print("❌ Revenue summary failed")
        
    else:
        print("❌ Authentication failed")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🎯 Basic Billing System Test Complete!")
