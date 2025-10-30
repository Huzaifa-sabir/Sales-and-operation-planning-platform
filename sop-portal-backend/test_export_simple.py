#!/usr/bin/env python3
"""
Simple test for export endpoint
"""
import requests
import json

def test_export_simple():
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
        print(f"Token: {token[:20]}...")
        
        # Test export endpoint
        print("\n2. Testing export endpoint...")
        export_response = requests.get(
            "http://localhost:8000/api/v1/excel/export/customers",
            headers=headers,
            timeout=30
        )
        
        print(f"Export Status: {export_response.status_code}")
        print(f"Response Headers: {dict(export_response.headers)}")
        
        if export_response.status_code == 200:
            print("✅ Export successful")
            print(f"Content-Type: {export_response.headers.get('content-type')}")
            print(f"Content-Length: {len(export_response.content)}")
        else:
            print(f"❌ Export failed: {export_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_export_simple()

