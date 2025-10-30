#!/usr/bin/env python3
"""
Test Excel forecast import/export functionality
"""
import requests
import json

def test_excel_forecasts():
    print("=== Testing Excel Forecast Functionality ===\n")
    
    # Step 1: Login
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
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Get active cycle
    print("\n2. Getting active cycle...")
    cycle_response = requests.get("http://localhost:8000/api/v1/sop/cycles/active", headers=headers)
    print(f"   Cycle status: {cycle_response.status_code}")
    
    if cycle_response.status_code != 200:
        print(f"   No active cycle found: {cycle_response.text}")
        return
    
    cycle_data = cycle_response.json()
    cycle_id = cycle_data["_id"]
    print(f"   ✅ Active cycle: {cycle_data['cycleName']} (ID: {cycle_id})")
    
    # Step 3: Test template download
    print("\n3. Testing template download...")
    template_response = requests.get(f"http://localhost:8000/api/v1/forecasts/cycle/{cycle_id}/template", headers=headers)
    print(f"   Template status: {template_response.status_code}")
    
    if template_response.status_code == 200:
        print(f"   ✅ Template downloaded successfully ({len(template_response.content)} bytes)")
    else:
        print(f"   ❌ Template download failed: {template_response.text}")
    
    # Step 4: Test export
    print("\n4. Testing forecast export...")
    export_response = requests.get(f"http://localhost:8000/api/v1/forecasts/cycle/{cycle_id}/export", headers=headers)
    print(f"   Export status: {export_response.status_code}")
    
    if export_response.status_code == 200:
        print(f"   ✅ Export successful ({len(export_response.content)} bytes)")
    else:
        print(f"   ❌ Export failed: {export_response.text}")

if __name__ == "__main__":
    test_excel_forecasts()

