#!/usr/bin/env python3
"""
Test products API endpoint
"""
import requests
import json

# Test login to get token
login_url = "http://localhost:8000/api/v1/auth/login"
login_data = {
    "email": "admin@heavygarlic.com",
    "password": "admin123"
}

print("Testing login...")
login_response = requests.post(login_url, json=login_data)
print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    token_data = login_response.json()
    token = token_data["access_token"]
    print(f"Got token: {token[:20]}...")
    
    # Test products API
    products_url = "http://localhost:8000/api/v1/products"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test with different parameters
    test_params = [
        {"page": 1, "limit": 10, "isActive": True},
        {"page": 1, "limit": 100, "isActive": True},
        {"page": 1, "limit": 10},
        {"page": 1, "limit": 100}
    ]
    
    for i, params in enumerate(test_params):
        print(f"\nTest {i+1}: {params}")
        response = requests.get(products_url, headers=headers, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            data = response.json()
            print(f"Products count: {len(data.get('products', []))}")
            print(f"Total: {data.get('total', 0)}")
else:
    print(f"Login failed: {login_response.text}")