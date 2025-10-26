"""
Test backend health and basic functionality
"""
import requests
import time

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("TESTING BACKEND HEALTH AND BASIC FUNCTIONALITY")
print("=" * 80)

# Test basic health
print("\n1. Testing backend health...")
try:
    health_response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=10)
    print(f"   Health check status: {health_response.status_code}")
    if health_response.status_code == 200:
        print(f"   ✅ Backend is healthy")
    else:
        print(f"   ❌ Backend health check failed")
except Exception as e:
    print(f"   ❌ Backend health check error: {e}")

# Test login
print("\n2. Testing admin login...")
try:
    admin_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@heavygarlic.com", "password": "admin123"},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"   Login status: {admin_response.status_code}")
    print(f"   Response headers: {dict(admin_response.headers)}")
    print(f"   Response text: {admin_response.text[:200]}")
    
    if admin_response.status_code == 200:
        admin_data = admin_response.json()
        admin_token = admin_data.get("access_token")
        print(f"   ✅ Login successful, token length: {len(admin_token) if admin_token else 0}")
        
        # Test sales statistics
        print(f"\n3. Testing sales statistics...")
        stats_response = requests.get(
            f"{BASE_URL}/sales-history/statistics?year=2024&month=11",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10
        )
        
        print(f"   Stats status: {stats_response.status_code}")
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print(f"   ✅ Sales Statistics Working:")
            print(f"     Total Revenue: ${stats_data.get('totalRevenue', 0):.2f}")
            print(f"     Total Quantity: {stats_data.get('totalQuantity', 0)}")
            print(f"     Record Count: {stats_data.get('recordCount', 0)}")
        else:
            print(f"   ❌ Sales Statistics Failed: {stats_response.text[:200]}")
        
        # Test simple report generation
        print(f"\n4. Testing simple report generation...")
        instant_response = requests.post(
            f"{BASE_URL}/reports/generate-instant",
            json={
                "reportType": "sales_summary",
                "format": "excel",
                "includeCharts": False,
                "includeRawData": True
            },
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"   Report status: {instant_response.status_code}")
        if instant_response.status_code == 200:
            print(f"   ✅ Report generation successful!")
            print(f"   Content-Type: {instant_response.headers.get('content-type', 'N/A')}")
            print(f"   File size: {len(instant_response.content)} bytes")
        else:
            print(f"   ❌ Report generation failed: {instant_response.text[:200]}")
            
    else:
        print(f"   ❌ Login failed")
        
except Exception as e:
    print(f"   ❌ Login test failed: {e}")

print(f"\n" + "=" * 80)
print("BACKEND HEALTH TEST COMPLETE")
print("=" * 80)
