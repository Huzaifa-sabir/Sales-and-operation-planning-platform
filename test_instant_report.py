"""
Test script for instant report generation endpoint
"""
import requests
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

# Get token (replace with actual login)
def get_auth_token():
    """Login and get authentication token"""
    login_data = {
        "email": "admin@sopportal.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_instant_report_generation(token):
    """Test instant report generation"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Test Sales Summary Report
    report_data = {
        "reportType": "sales_summary",
        "format": "excel",
        "includeCharts": True,
        "includeRawData": False
    }

    print("\n" + "="*60)
    print("Testing Instant Report Generation")
    print("="*60)
    print(f"Report Type: {report_data['reportType']}")
    print(f"Format: {report_data['format']}")

    try:
        print("\n Sending request to /reports/generate-instant...")
        response = requests.post(
            f"{BASE_URL}/reports/generate-instant",
            headers=headers,
            json=report_data,
            timeout=60  # 60 second timeout
        )

        print(f"✓ Response Status: {response.status_code}")

        if response.status_code == 200:
            print(f"✓ Content Type: {response.headers.get('content-type')}")
            print(f"✓ Content Length: {len(response.content)} bytes")

            # Save file
            filename = f"test_sales_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✓ File saved: {filename}")
            print(f"✓ File size: {os.path.getsize(filename)} bytes")

            print("\n✅ SUCCESS: Report generated and downloaded instantly!")
            return True
        else:
            print(f"\n❌ FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("\n❌ FAILED: Request timed out (> 60 seconds)")
        return False
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False

def main():
    print("Starting Report Generation Test")
    print("-" * 60)

    # Get authentication token
    print("\n1. Authenticating...")
    token = get_auth_token()

    if not token:
        print("❌ Failed to authenticate")
        return

    print("✓ Authentication successful")

    # Test instant report generation
    print("\n2. Testing instant report generation...")
    success = test_instant_report_generation(token)

    if success:
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✅")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("TESTS FAILED ❌")
        print("="*60)

if __name__ == "__main__":
    main()
