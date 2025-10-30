#!/usr/bin/env python3
"""
Test login with username instead of email
"""
import requests
import json

def test_login():
    try:
        # Test login with admin credentials using username
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        print("Testing login with username:")
        print(f"Username: {login_data['username']}")
        print(f"Password: {login_data['password']}")
        print()
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nLogin successful!")
            print(f"User: {data.get('user', {}).get('username')}")
            print(f"Role: {data.get('user', {}).get('role')}")
        else:
            print(f"\nLogin failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error response: {response.text}")
            
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    test_login()

