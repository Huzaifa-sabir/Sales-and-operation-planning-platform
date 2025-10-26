"""
Check backend health and investigate 502 errors
"""
import requests
import time

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("INVESTIGATING BACKEND HEALTH AND 502 ERRORS")
print("=" * 80)

# Test basic health
print("\n1. Testing backend health...")
try:
    health_response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=10)
    print(f"   Health check status: {health_response.status_code}")
    if health_response.status_code == 200:
        print(f"   ✅ Backend is healthy")
    else:
        print(f"   ❌ Backend health check failed: {health_response.text[:200]}")
except Exception as e:
    print(f"   ❌ Backend health check error: {e}")

# Test basic login
print("\n2. Testing basic login...")
try:
    admin_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@heavygarlic.com", "password": "admin123"},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"   Login status: {admin_response.status_code}")
    if admin_response.status_code == 200:
        admin_data = admin_response.json()
        admin_token = admin_data.get("access_token")
        print(f"   ✅ Login successful, token length: {len(admin_token) if admin_token else 0}")
        
        # Test simple sales statistics
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
        
        # Test simple report generation (no filters)
        print(f"\n4. Testing simple report generation...")
        simple_report_response = requests.post(
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
        
        print(f"   Simple report status: {simple_report_response.status_code}")
        if simple_report_response.status_code == 200:
            print(f"   ✅ Simple report generation successful!")
            print(f"   Content-Type: {simple_report_response.headers.get('content-type', 'N/A')}")
            print(f"   File size: {len(simple_report_response.content)} bytes")
        else:
            print(f"   ❌ Simple report generation failed: {simple_report_response.text[:200]}")
            
    else:
        print(f"   ❌ Login failed: {admin_response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Test failed: {e}")

print(f"\n" + "=" * 80)
print("BACKEND HEALTH INVESTIGATION COMPLETE")
print("=" * 80)

# Analysis
print(f"\n🔍 ANALYSIS:")
if 'Login successful' in str(locals()):
    print(f"✅ Backend is running and login works")
    if 'Simple report generation successful!' in str(locals()):
        print(f"✅ Basic report generation works")
        print(f"❌ Issue might be with PDF generation or date filtering logic")
    else:
        print(f"❌ Report generation is broken - might be deployment issue")
else:
    print(f"❌ Backend is not responding properly - deployment issue")
