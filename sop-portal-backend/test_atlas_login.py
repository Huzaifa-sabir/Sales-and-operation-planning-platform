#!/usr/bin/env python3
"""
Test login with MongoDB Atlas database
"""
import requests
import json

def test_login():
    """Test login endpoint with Atlas database"""
    url = "http://localhost:8000/api/v1/auth/login"
    data = {
        "username": "admin@heavygarlic.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Login successful with Atlas database!")
            return True
        else:
            print("❌ Login failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_health():
    """Test health endpoint"""
    url = "http://localhost:8000/health"
    
    try:
        response = requests.get(url)
        print(f"Health Status: {response.json()}")
        return True
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing MongoDB Atlas Integration")
    print("=" * 40)
    
    print("\n1. Testing Health Endpoint:")
    test_health()
    
    print("\n2. Testing Login:")
    test_login()

