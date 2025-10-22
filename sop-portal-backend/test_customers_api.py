#!/usr/bin/env python3
"""
Test customers API endpoints
"""
import requests
import json
import time

def test_customers_api():
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
            print(f"✅ GET successful - Found {len(data.get('data', []))} customers")
        else:
            print(f"❌ GET failed: {get_response.text}")
        
        # Test POST customers
        print("\n3. Testing POST /api/v1/customers...")
        customer_data = {
            "customerId": f"TEST-{int(time.time())}",
            "customerName": "Test Customer",
            "location": {
                "city": "Test City",
                "state": "TS",
                "address": "123 Test St",
                "zipCode": "12345",
                "country": "USA"
            },
            "contactPerson": "Test Person"
        }
        
        post_response = requests.post(
            "http://localhost:8000/api/v1/customers",
            json=customer_data,
            headers=headers,
            timeout=10
        )
        
        print(f"POST Status: {post_response.status_code}")
        if post_response.status_code == 200 or post_response.status_code == 201:
            print("✅ POST successful")
            print(f"Response: {post_response.json()}")
        else:
            print(f"❌ POST failed: {post_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_customers_api()
