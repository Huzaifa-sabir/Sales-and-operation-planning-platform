#!/usr/bin/env python3
"""
Test API response structure
"""
import requests
import json

def test_api_response():
    try:
        # First login to get token
        login_data = {
            "email": "admin@heavygarlic.com",
            "password": "admin123"
        }
        
        print("1. Testing login...")
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code} - {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print("✅ Login successful")
        
        # Test GET customers
        print("\n2. Testing GET /api/v1/customers...")
        get_response = requests.get(
            "http://localhost:8000/api/v1/customers",
            headers=headers,
            timeout=10
        )
        
        print(f"GET Status: {get_response.status_code}")
        if get_response.status_code == 200:
            data = get_response.json()
            print(f"✅ GET successful")
            print(f"Response structure:")
            print(f"  Keys: {list(data.keys())}")
            print(f"  customers type: {type(data.get('customers'))}")
            print(f"  customers length: {len(data.get('customers', []))}")
            print(f"  total: {data.get('total')}")
            print(f"  page: {data.get('page')}")
            print(f"  pageSize: {data.get('pageSize')}")
            
            if data.get('customers'):
                print(f"\nFirst customer structure:")
                first_customer = data['customers'][0]
                print(f"  Keys: {list(first_customer.keys())}")
                print(f"  customerId: {first_customer.get('customerId')}")
                print(f"  customerName: {first_customer.get('customerName')}")
        else:
            print(f"❌ GET failed: {get_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_response()

