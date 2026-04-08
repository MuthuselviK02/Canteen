#!/usr/bin/env python3
"""
🧪 SMART CANTEEN COMPREHENSIVE TESTING SUITE
Run this script to test all major functionalities
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8081"

# Test Results
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": []
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{title.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.END}")

def run_test(test_name, test_func):
    """Run a single test and track results"""
    test_results["total"] += 1
    try:
        print(f"\n🧪 {test_name}...")
        result = test_func()
        if result:
            print_success(f"{test_name} - PASSED")
            test_results["passed"] += 1
        else:
            print_error(f"{test_name} - FAILED")
            test_results["failed"] += 1
            test_results["errors"].append(f"{test_name} - FAILED")
    except Exception as e:
        print_error(f"{test_name} - ERROR: {str(e)}")
        test_results["failed"] += 1
        test_results["errors"].append(f"{test_name} - ERROR: {str(e)}")

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('status') == 'running'
        return False
    except Exception as e:
        print(f"   Debug: Backend health error - {str(e)}")
        return False

def test_frontend_health():
    """Test if frontend is running"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        return response.status_code == 200
    except:
        return False

def test_user_registration():
    """Test user registration"""
    timestamp = int(time.time())
    test_user = {
        "fullname": f"Test User {timestamp}",
        "email": f"test{timestamp}@example.com",
        "password": "test123456"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
    
    if response.status_code == 200:
        user_data = response.json()
        return user_data.get('email') == test_user['email']
    return False

def test_user_login():
    """Test user login"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "sharan@gmail.com",
        "password": "sharan@1230"
    })
    
    if response.status_code == 200:
        data = response.json()
        return 'access_token' in data
    return False

def test_menu_api():
    """Test menu API"""
    response = requests.get(f"{BASE_URL}/api/menu/")
    
    if response.status_code == 200:
        menu_items = response.json()
        return len(menu_items) > 0
    return False

def test_ai_recommendations():
    """Test AI recommendations"""
    # Login first
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "sharan@gmail.com",
        "password": "sharan@1230"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test AI recommendations
        ai_response = requests.get(f"{BASE_URL}/api/ai/recommendations/all", headers=headers)
        
        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            return 'recommendations' in ai_data and len(ai_data['recommendations']) > 0
    
    return False

def test_ai_recommendations_saran():
    """Test AI recommendations for Saran (was failing before)"""
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "saran@gmail.com",
        "password": "saran@1230"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        ai_response = requests.get(f"{BASE_URL}/api/ai/recommendations/all", headers=headers)
        
        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            return 'recommendations' in ai_data and len(ai_data['recommendations']) > 0
    
    return False

def test_order_creation():
    """Test order creation"""
    # Login first
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "sharan@gmail.com",
        "password": "sharan@1230"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get menu items
        menu_response = requests.get(f"{BASE_URL}/api/menu/", headers=headers)
        
        if menu_response.status_code == 200:
            menu_items = menu_response.json()
            if len(menu_items) > 0:
                # Create order with first item
                order_data = {
                    "items": [
                        {
                            "menu_item_id": menu_items[0]['id'],
                            "quantity": 1
                        }
                    ],
                    "notes": "Test order"
                }
                
                order_response = requests.post(f"{BASE_URL}/api/orders/", json=order_data, headers=headers)
                
                return order_response.status_code in [200, 201]
    
    return False

def test_billing_invoices():
    """Test billing invoices"""
    # Login as admin or user with billing access
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "sharan@gmail.com",
        "password": "sharan@1230"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test billing invoices
        billing_response = requests.get(f"{BASE_URL}/api/billing/invoices", headers=headers)
        
        return billing_response.status_code == 200
    
    return False

def test_database_connection():
    """Test database connection"""
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            'Authorization': 'Bearer invalid_token'
        })
        # Should return 401, not 500, indicating database is connected
        return response.status_code == 401
    except:
        return False

def test_cors_configuration():
    """Test CORS configuration"""
    try:
        response = requests.options(f"{BASE_URL}/api/auth/login", 
                                  headers={'Origin': FRONTEND_URL})
        return response.status_code < 500
    except:
        return False

def test_auto_login_registration():
    """Test auto-login after registration"""
    timestamp = int(time.time())
    test_user = {
        "fullname": f"Auto User {timestamp}",
        "email": f"auto{timestamp}@example.com",
        "password": "test123456"
    }
    
    # Register user
    register_response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
    
    if register_response.status_code == 200:
        # Try to login immediately
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        
        return login_response.status_code == 200
    
    return False

def test_duplicate_registration():
    """Test duplicate registration prevention"""
    # Try to register with existing email
    duplicate_response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "fullname": "Duplicate Test",
        "email": "sharan@gmail.com",  # Existing user
        "password": "test123456"
    })
    
    return duplicate_response.status_code == 400  # Should fail

def test_role_based_access():
    """Test role-based access control"""
    # Test user access
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "sharan@gmail.com",
        "password": "sharan@1230"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test user-specific endpoints
        orders_response = requests.get(f"{BASE_URL}/api/orders/", headers=headers)
        
        return orders_response.status_code == 200
    
    return False

def run_comprehensive_tests():
    """Run all tests"""
    print_header("🧪 SMART CANTEEN COMPREHENSIVE TESTING SUITE")
    print_info(f"Testing Backend: {BASE_URL}")
    print_info(f"Testing Frontend: {FRONTEND_URL}")
    print_info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # System Health Tests
    print_header("🏥 SYSTEM HEALTH TESTS")
    run_test("Backend Health Check", test_backend_health)
    run_test("Frontend Health Check", test_frontend_health)
    run_test("Database Connection", test_database_connection)
    run_test("CORS Configuration", test_cors_configuration)
    
    # Authentication Tests
    print_header("🔐 AUTHENTICATION TESTS")
    run_test("User Registration", test_user_registration)
    run_test("User Login", test_user_login)
    run_test("Auto-Login Registration", test_auto_login_registration)
    run_test("Duplicate Registration Prevention", test_duplicate_registration)
    run_test("Role-Based Access", test_role_based_access)
    
    # Core Functionality Tests
    print_header("🍽️ CORE FUNCTIONALITY TESTS")
    run_test("Menu API", test_menu_api)
    run_test("Order Creation", test_order_creation)
    run_test("Billing Invoices", test_billing_invoices)
    
    # AI Recommendations Tests
    print_header("🤖 AI RECOMMENDATIONS TESTS")
    run_test("AI Recommendations (Sharan)", test_ai_recommendations)
    run_test("AI Recommendations (Saran)", test_ai_recommendations_saran)
    
    # Print Results
    print_header("📊 TEST RESULTS")
    print_info(f"Total Tests: {test_results['total']}")
    print_success(f"Passed: {test_results['passed']}")
    print_error(f"Failed: {test_results['failed']}")
    
    success_rate = (test_results['passed'] / test_results['total']) * 100 if test_results['total'] > 0 else 0
    print_info(f"Success Rate: {success_rate:.1f}%")
    
    if test_results['errors']:
        print_header("❌ FAILED TESTS")
        for error in test_results['errors']:
            print_error(error)
    
    # Overall Status
    print_header("🎯 OVERALL STATUS")
    if test_results['failed'] == 0:
        print_success("🎉 ALL TESTS PASSED - READY FOR PRODUCTION!")
    elif test_results['failed'] <= test_results['total'] * 0.1:  # Less than 10% failure
        print_warning("⚠️ MOSTLY READY - Minor issues to fix")
    else:
        print_error("❌ NOT READY - Major issues need to be addressed")
    
    return test_results['failed'] == 0

if __name__ == "__main__":
    try:
        success = run_comprehensive_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_warning("\n\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\n❌ Testing suite error: {str(e)}")
        sys.exit(1)
