#!/usr/bin/env python3
"""
Test authentication and role
"""
import requests
import json

def test_auth_role():
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
        user_data = login_response.json()["user"]
        
        print("✅ Login successful")
        print(f"User: {user_data.get('username')}")
        print(f"Role: {user_data.get('role')}")
        print(f"Email: {user_data.get('email')}")
        
        # Test auth/me endpoint
        print("\n2. Testing auth/me endpoint...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        me_response = requests.get(
            "http://localhost:8000/api/v1/auth/me",
            headers=headers,
            timeout=5
        )
        
        print(f"Auth/me Status: {me_response.status_code}")
        if me_response.status_code == 200:
            me_data = me_response.json()
            print(f"✅ Auth/me successful")
            print(f"User: {me_data.get('username')}")
            print(f"Role: {me_data.get('role')}")
        else:
            print(f"❌ Auth/me failed: {me_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_auth_role()
