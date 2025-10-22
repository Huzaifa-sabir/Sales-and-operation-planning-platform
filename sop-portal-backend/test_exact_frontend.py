#!/usr/bin/env python3
"""
Test login with exact frontend format
"""
import requests
import json

def test_exact_frontend():
    try:
        # Test with email field (as frontend should send)
        login_data_email = {
            "email": "admin@heavygarlic.com",
            "password": "admin123"
        }
        
        print("Testing with email field:")
        print(f"Email: {login_data_email['email']}")
        print(f"Password: {login_data_email['password']}")
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data_email,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS with email field!")
        else:
            print(f"Failed with email field: {response.text}")
        
        print("\n" + "="*50 + "\n")
        
        # Test with username field containing email
        login_data_username = {
            "username": "admin@heavygarlic.com",
            "password": "admin123"
        }
        
        print("Testing with username field (email):")
        print(f"Username: {login_data_username['username']}")
        print(f"Password: {login_data_username['password']}")
        
        response2 = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data_username,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response2.status_code}")
        if response2.status_code == 200:
            print("SUCCESS with username field!")
        else:
            print(f"Failed with username field: {response2.text}")
            
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    test_exact_frontend()
