#!/usr/bin/env python3
"""
Test full authentication and products flow
"""
import requests
import json

def test_full_flow():
    print("=== Testing Full Authentication Flow ===\n")
    
    # Step 1: Test login
    print("1. Testing login...")
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {
        "email": "admin@heavygarlic.com",
        "password": "admin123"
    }
    
    login_response = requests.post(login_url, json=login_data)
    print(f"   Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"   Login failed: {login_response.text}")
        return
    
    token_data = login_response.json()
    token = token_data["access_token"]
    print(f"   ✅ Got token: {token[:20]}...")
    
    # Step 2: Test products API with token
    print("\n2. Testing products API...")
    products_url = "http://localhost:8000/api/v1/products"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test the exact parameters the frontend is sending
    params = {
        "page": 1,
        "limit": 100,
        "isActive": True
    }
    
    print(f"   Requesting: {products_url} with params: {params}")
    response = requests.get(products_url, headers=headers, params=params)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success! Products count: {len(data.get('products', []))}")
        print(f"   Total: {data.get('total', 0)}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Step 3: Test without token (should fail)
    print("\n3. Testing products API without token...")
    response_no_token = requests.get(products_url, params=params)
    print(f"   Status: {response_no_token.status_code}")
    if response_no_token.status_code == 401:
        print("   ✅ Correctly rejected without token")
    else:
        print(f"   ❌ Unexpected response: {response_no_token.text}")

if __name__ == "__main__":
    test_full_flow()

