"""
Test authentication endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """Test login endpoint"""
    print("=" * 60)
    print("TEST 1: Login with Admin Credentials")
    print("=" * 60)

    login_data = {
        "username": "admin",
        "password": "admin123"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("[OK] Login successful!")
        print(f"Token: {data['access_token'][:50]}...")
        print(f"Token Type: {data['token_type']}")
        print(f"Expires In: {data['expires_in']} seconds")
        print(f"User: {data['user']}")
        return data['access_token']
    else:
        print(f"[FAIL] Login failed: {response.json()}")
        return None


def test_get_me(token):
    """Test get current user endpoint"""
    print("\n" + "=" * 60)
    print("TEST 2: Get Current User (/auth/me)")
    print("=" * 60)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("[OK] User info retrieved successfully!")
        print(json.dumps(data, indent=2))
    else:
        print(f"[FAIL] Failed: {response.json()}")


def test_invalid_login():
    """Test login with invalid credentials"""
    print("\n" + "=" * 60)
    print("TEST 3: Login with Invalid Credentials")
    print("=" * 60)

    login_data = {
        "username": "admin",
        "password": "wrongpassword"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 401:
        print("[OK] Correctly rejected invalid credentials!")
        print(f"Error: {response.json()['detail']}")
    else:
        print(f"[FAIL] Unexpected response: {response.json()}")


def test_no_token():
    """Test protected endpoint without token"""
    print("\n" + "=" * 60)
    print("TEST 4: Access Protected Endpoint Without Token")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/auth/me")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 403:
        print("[OK] Correctly rejected request without token!")
        print(f"Error: {response.json()['detail']}")
    else:
        print(f"Response: {response.json()}")


def test_refresh_token(token):
    """Test token refresh endpoint"""
    print("\n" + "=" * 60)
    print("TEST 5: Refresh Token")
    print("=" * 60)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(f"{BASE_URL}/auth/refresh", headers=headers)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("[OK] Token refreshed successfully!")
        print(f"New Token: {data['access_token'][:50]}...")
    else:
        print(f"[FAIL] Failed: {response.json()}")


def test_sales_rep_login():
    """Test login with sales rep credentials"""
    print("\n" + "=" * 60)
    print("TEST 6: Login with Sales Rep Credentials")
    print("=" * 60)

    login_data = {
        "username": "sales",
        "password": "sales123"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("[OK] Sales rep login successful!")
        print(f"User: {data['user']}")
        return data['access_token']
    else:
        print(f"[FAIL] Login failed: {response.json()}")
        return None


def main():
    """Run all tests"""
    print("\nStarting Authentication Tests...")
    print("=" * 60)

    try:
        # Test 1: Admin login
        admin_token = test_login()

        if admin_token:
            # Test 2: Get current user
            test_get_me(admin_token)

            # Test 5: Refresh token
            test_refresh_token(admin_token)

        # Test 3: Invalid credentials
        test_invalid_login()

        # Test 4: No token
        test_no_token()

        # Test 6: Sales rep login
        sales_token = test_sales_rep_login()
        if sales_token:
            test_get_me(sales_token)

        print("\n" + "=" * 60)
        print("All authentication tests completed!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to backend server at http://localhost:8000")
        print("Please make sure the backend server is running.")
    except Exception as e:
        print(f"\nERROR: {str(e)}")


if __name__ == "__main__":
    main()
