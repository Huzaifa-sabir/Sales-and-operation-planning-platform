#!/usr/bin/env python3
"""
Simple test for GET customers
"""
import requests
import json

def test_simple_get():
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
            timeout=5
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
        
        # Test GET customers with minimal timeout
        print("\n2. Testing GET /api/v1/customers...")
        get_response = requests.get(
            "http://localhost:8000/api/v1/customers?page=1&pageSize=5",
            headers=headers,
            timeout=5
        )
        
        print(f"GET Status: {get_response.status_code}")
        if get_response.status_code == 200:
            data = get_response.json()
            print(f"✅ GET successful")
            print(f"Total customers: {data.get('total')}")
            print(f"Customers returned: {len(data.get('customers', []))}")
            if data.get('customers'):
                print(f"First customer: {data['customers'][0].get('customerId')} - {data['customers'][0].get('customerName')}")
        else:
            print(f"❌ GET failed: {get_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple_get()
