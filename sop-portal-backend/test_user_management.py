"""
Test script for User Management API endpoints
Tests all CRUD operations, filtering, pagination, and password reset
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Global variables to store tokens and created user IDs
admin_token = None
created_user_ids = []
reset_token = None


def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print formatted test result"""
    status = "[OK]" if success else "[FAIL]"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")
    print()


def login_as_admin():
    """Login as admin to get access token"""
    global admin_token
    print("=" * 60)
    print("AUTHENTICATION")
    print("=" * 60)

    url = f"{BASE_URL}/auth/login"
    payload = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            admin_token = data["access_token"]
            print_test_result(
                "Admin Login",
                True,
                f"Token received: {admin_token[:20]}..."
            )
            return True
        else:
            print_test_result(
                "Admin Login",
                False,
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False
    except Exception as e:
        print_test_result("Admin Login", False, f"Error: {str(e)}")
        return False


def test_create_user():
    """Test creating a new user"""
    print("=" * 60)
    print("TEST 1: Create New User")
    print("=" * 60)

    url = f"{BASE_URL}/users"
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
        "email": f"testuser_{datetime.now().strftime('%H%M%S')}@example.com",
        "fullName": "Test User",
        "role": "sales_rep"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            data = response.json()
            user_id = data["user"]["id"]
            created_user_ids.append(user_id)
            print_test_result(
                "Create User",
                True,
                f"User ID: {user_id}, Generated Password: {data['generatedPassword']}"
            )
            return True, data
        else:
            print_test_result(
                "Create User",
                False,
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False, None
    except Exception as e:
        print_test_result("Create User", False, f"Error: {str(e)}")
        return False, None


def test_list_users():
    """Test listing users with pagination"""
    print("=" * 60)
    print("TEST 2: List Users with Pagination")
    print("=" * 60)

    url = f"{BASE_URL}/users?page=1&pageSize=5"
    headers = {"Authorization": f"Bearer {admin_token}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_test_result(
                "List Users",
                True,
                f"Total: {data['total']}, Page: {data['page']}/{data['totalPages']}, "
                f"Users in this page: {len(data['users'])}"
            )
            print(f"    Users: {[u['username'] for u in data['users']]}")
            return True, data
        else:
            print_test_result(
                "List Users",
                False,
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False, None
    except Exception as e:
        print_test_result("List Users", False, f"Error: {str(e)}")
        return False, None


def test_filter_users_by_role():
    """Test filtering users by role"""
    print("=" * 60)
    print("TEST 3: Filter Users by Role")
    print("=" * 60)

    url = f"{BASE_URL}/users?role=sales_rep"
    headers = {"Authorization": f"Bearer {admin_token}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            all_sales_reps = all(u["role"] == "sales_rep" for u in data["users"])
            print_test_result(
                "Filter by Role",
                all_sales_reps,
                f"Found {data['total']} sales reps, All sales_rep: {all_sales_reps}"
            )
            return all_sales_reps, data
        else:
            print_test_result(
                "Filter by Role",
                False,
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False, None
    except Exception as e:
        print_test_result("Filter by Role", False, f"Error: {str(e)}")
        return False, None


def test_search_users():
    """Test searching users"""
    print("=" * 60)
    print("TEST 4: Search Users")
    print("=" * 60)

    url = f"{BASE_URL}/users?search=admin"
    headers = {"Authorization": f"Bearer {admin_token}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            found_admin = any("admin" in u["username"].lower() for u in data["users"])
            print_test_result(
                "Search Users",
                found_admin,
                f"Search 'admin' found {data['total']} users"
            )
            return found_admin, data
        else:
            print_test_result(
                "Search Users",
                False,
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False, None
    except Exception as e:
        print_test_result("Search Users", False, f"Error: {str(e)}")
        return False, None


def test_get_user_by_id():
    """Test getting a specific user by ID"""
    print("=" * 60)
    print("TEST 5: Get User by ID")
    print("=" * 60)

    if not created_user_ids:
        print_test_result("Get User by ID", False, "No user ID available")
        return False, None

    user_id = created_user_ids[0]
    url = f"{BASE_URL}/users/{user_id}"
    headers = {"Authorization": f"Bearer {admin_token}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_test_result(
                "Get User by ID",
                True,
                f"Username: {data['username']}, Email: {data['email']}"
            )
            return True, data
        else:
            print_test_result(
                "Get User by ID",
                False,
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False, None
    except Exception as e:
        print_test_result("Get User by ID", False, f"Error: {str(e)}")
        return False, None


def test_update_user():
    """Test updating user information"""
    print("=" * 60)
    print("TEST 6: Update User")
    print("=" * 60)

    if not created_user_ids:
        print_test_result("Update User", False, "No user ID available")
        return False, None

    user_id = created_user_ids[0]
    url = f"{BASE_URL}/users/{user_id}"
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "fullName": "Updated Test User Name"
    }

    try:
        response = requests.put(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_test_result(
                "Update User",
                data["fullName"] == "Updated Test User Name",
                f"New Full Name: {data['fullName']}"
            )
            return True, data
        else:
            print_test_result(
                "Update User",
                False,
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False, None
    except Exception as e:
        print_test_result("Update User", False, f"Error: {str(e)}")
        return False, None


def test_toggle_user_status():
    """Test toggling user active status"""
    print("=" * 60)
    print("TEST 7: Toggle User Status")
    print("=" * 60)

    if not created_user_ids:
        print_test_result("Toggle User Status", False, "No user ID available")
        return False, None

    user_id = created_user_ids[0]
    url = f"{BASE_URL}/users/{user_id}/toggle-status"
    headers = {"Authorization": f"Bearer {admin_token}"}

    try:
        # First toggle (should deactivate)
        response = requests.patch(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            is_inactive = not data["isActive"]
            print_test_result(
                "Toggle User Status (Deactivate)",
                is_inactive,
                f"User is now {'inactive' if not data['isActive'] else 'active'}"
            )

            # Second toggle (should reactivate)
            response = requests.patch(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                is_active = data["isActive"]
                print_test_result(
                    "Toggle User Status (Reactivate)",
                    is_active,
                    f"User is now {'active' if data['isActive'] else 'inactive'}"
                )
                return True, data
        else:
            print_test_result(
                "Toggle User Status",
                False,
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False, None
    except Exception as e:
        print_test_result("Toggle User Status", False, f"Error: {str(e)}")
        return False, None


def test_password_reset_request():
    """Test requesting password reset"""
    print("=" * 60)
    print("TEST 8: Request Password Reset")
    print("=" * 60)

    url = f"{BASE_URL}/users/password-reset/request"
    payload = {
        "email": "admin@sop-portal.com"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print_test_result(
                "Request Password Reset",
                True,
                f"Message: {data['message']}"
            )
            print("    Check server console for reset token")
            return True, data
        else:
            print_test_result(
                "Request Password Reset",
                False,
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False, None
    except Exception as e:
        print_test_result("Request Password Reset", False, f"Error: {str(e)}")
        return False, None


def test_password_reset_confirm():
    """Test confirming password reset with token"""
    print("=" * 60)
    print("TEST 9: Confirm Password Reset")
    print("=" * 60)

    print("Note: This test requires manual token input from server console")
    print("Skipping automatic test. To test manually:")
    print("1. Run the password reset request test")
    print("2. Copy the token from server console")
    print("3. Make a POST request to /api/v1/users/password-reset/confirm")
    print("   with body: {\"token\": \"<token>\", \"newPassword\": \"NewPass123!\"}")
    print()


def test_cannot_delete_last_admin():
    """Test that last admin cannot be deleted"""
    print("=" * 60)
    print("TEST 10: Cannot Delete Last Admin")
    print("=" * 60)

    # First, get the admin user ID
    url = f"{BASE_URL}/users?role=admin"
    headers = {"Authorization": f"Bearer {admin_token}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["total"] == 1:
                admin_id = data["users"][0]["id"]

                # Try to delete the last admin
                delete_url = f"{BASE_URL}/users/{admin_id}"
                delete_response = requests.delete(delete_url, headers=headers)

                # Should fail with 400
                success = delete_response.status_code == 400
                print_test_result(
                    "Cannot Delete Last Admin",
                    success,
                    f"Status: {delete_response.status_code}, "
                    f"Expected 400 (validation prevents deletion)"
                )
                return success, None
            else:
                print_test_result(
                    "Cannot Delete Last Admin",
                    False,
                    f"Multiple admins exist ({data['total']}), cannot test"
                )
                return False, None
        else:
            print_test_result(
                "Cannot Delete Last Admin",
                False,
                f"Status: {response.status_code}"
            )
            return False, None
    except Exception as e:
        print_test_result("Cannot Delete Last Admin", False, f"Error: {str(e)}")
        return False, None


def test_delete_user():
    """Test deleting a user"""
    print("=" * 60)
    print("TEST 11: Delete User")
    print("=" * 60)

    if not created_user_ids:
        print_test_result("Delete User", False, "No user ID available")
        return False, None

    user_id = created_user_ids[0]
    url = f"{BASE_URL}/users/{user_id}"
    headers = {"Authorization": f"Bearer {admin_token}"}

    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_test_result(
                "Delete User",
                data["success"],
                f"Message: {data['message']}"
            )
            return True, data
        else:
            print_test_result(
                "Delete User",
                False,
                f"Status: {response.status_code}, Response: {response.text}"
            )
            return False, None
    except Exception as e:
        print_test_result("Delete User", False, f"Error: {str(e)}")
        return False, None


def test_access_without_token():
    """Test that endpoints require authentication"""
    print("=" * 60)
    print("TEST 12: Access Without Token (Should Fail)")
    print("=" * 60)

    url = f"{BASE_URL}/users"

    try:
        response = requests.get(url)
        # Should fail with 403 (no token)
        success = response.status_code == 403
        print_test_result(
            "Access Without Token",
            success,
            f"Status: {response.status_code}, Expected 403"
        )
        return success, None
    except Exception as e:
        print_test_result("Access Without Token", False, f"Error: {str(e)}")
        return False, None


def main():
    """Run all tests"""
    print("\n")
    print("*" * 60)
    print("USER MANAGEMENT API - COMPREHENSIVE TEST SUITE")
    print("*" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print("*" * 60)
    print("\n")

    # Track test results
    results = []

    # Login first
    if not login_as_admin():
        print("Failed to login. Aborting tests.")
        return

    # Run all tests
    results.append(("Create User", test_create_user()[0]))
    results.append(("List Users", test_list_users()[0]))
    results.append(("Filter by Role", test_filter_users_by_role()[0]))
    results.append(("Search Users", test_search_users()[0]))
    results.append(("Get User by ID", test_get_user_by_id()[0]))
    results.append(("Update User", test_update_user()[0]))
    results.append(("Toggle User Status", test_toggle_user_status()[0]))
    results.append(("Request Password Reset", test_password_reset_request()[0]))
    test_password_reset_confirm()  # Manual test
    results.append(("Cannot Delete Last Admin", test_cannot_delete_last_admin()[0]))
    results.append(("Delete User", test_delete_user()[0]))
    results.append(("Access Without Token", test_access_without_token()[0]))

    # Print summary
    print("\n")
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    print()

    for test_name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    print("=" * 60)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
