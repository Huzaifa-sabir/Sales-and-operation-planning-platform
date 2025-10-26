"""
Test the exact scenario: Admin creates user, then user tries to login
This simulates the real-world scenario described by the user
"""
import requests
import json
import time

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("TESTING REAL-WORLD SCENARIO: ADMIN CREATES USER, USER LOGS IN")
print("=" * 80)

# Step 1: Login as admin
print("\n1. Logging in as admin...")
admin_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "admin@heavygarlic.com", "password": "admin123"},
    headers={"Content-Type": "application/json"}
)

if admin_response.status_code != 200:
    print(f"   [X] Admin login failed: {admin_response.status_code}")
    print(f"   Response: {admin_response.text}")
    exit(1)

admin_data = admin_response.json()
admin_token = admin_data.get("access_token")
print(f"   [OK] Admin logged in successfully")

# Step 2: Create a new user (simulating admin creating user via frontend)
print("\n2. Admin creating new user...")
timestamp = int(time.time())
test_username = f"realuser_{timestamp}"
test_email = f"realuser_{timestamp}@company.com"
test_password = "RealUserPass123!"  # This is what admin would set

print(f"   Creating user with:")
print(f"   - Username: {test_username}")
print(f"   - Email: {test_email}")
print(f"   - Password: {test_password}")

create_response = requests.post(
    f"{BASE_URL}/users",
    json={
        "username": test_username,
        "email": test_email,
        "fullName": "Real User Test",
        "role": "sales_rep",
        "password": test_password  # Admin sets this password
    },
    headers={
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
)

print(f"   Create response status: {create_response.status_code}")
if create_response.status_code != 201:
    print(f"   [X] User creation failed")
    print(f"   Response: {create_response.text}")
    exit(1)

create_data = create_response.json()
user_id = create_data['user']['_id']
print(f"   [OK] User created successfully")
print(f"   User ID: {user_id}")
print(f"   Generated password returned: {create_data.get('generatedPassword', 'NOT RETURNED')}")

# Step 3: Wait a moment (simulate real-world delay)
print("\n3. Waiting 2 seconds (simulating real-world delay)...")
time.sleep(2)

# Step 4: User tries to login with the credentials admin set
print("\n4. User attempting to login with admin-set credentials...")
print(f"   Login attempt with:")
print(f"   - Email: {test_email}")
print(f"   - Password: {test_password}")

login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": test_email,
        "password": test_password
    },
    headers={"Content-Type": "application/json"}
)

print(f"\n   Login response status: {login_response.status_code}")
print(f"   Login response: {login_response.text[:300]}")

if login_response.status_code == 200:
    login_data = login_response.json()
    print(f"\n   [SUCCESS] User login successful!")
    print(f"   Logged in as: {login_data['user']['username']}")
    print(f"   Role: {login_data['user']['role']}")
    print(f"   Token received: {len(login_data['access_token'])} characters")
else:
    print(f"\n   [FAILURE] User login failed!")
    print(f"   Status: {login_response.status_code}")
    print(f"   Error: {login_response.text}")

# Step 5: Test with different password formats (in case there's a password issue)
print("\n5. Testing password variations...")

# Test with the generated password if different
if create_data.get('generatedPassword') and create_data['generatedPassword'] != test_password:
    print(f"\n5a. Testing with generated password: {create_data['generatedPassword']}")
    gen_login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": test_email,
            "password": create_data['generatedPassword']
        },
        headers={"Content-Type": "application/json"}
    )
    print(f"   Generated password login status: {gen_login_response.status_code}")
    if gen_login_response.status_code == 200:
        print(f"   [SUCCESS] Generated password works!")
    else:
        print(f"   [FAILURE] Generated password failed: {gen_login_response.text[:100]}")

# Step 6: Check user status in database
print("\n6. Checking user status in database...")
user_check_response = requests.get(
    f"{BASE_URL}/users/{user_id}",
    headers={"Authorization": f"Bearer {admin_token}"}
)

if user_check_response.status_code == 200:
    user_data = user_check_response.json()
    print(f"   [OK] User found in database")
    print(f"   Username: {user_data['username']}")
    print(f"   Email: {user_data['email']}")
    print(f"   Is Active: {user_data['isActive']}")
    print(f"   Login Attempts: {user_data.get('loginAttempts', 'N/A')}")
    print(f"   Last Login: {user_data.get('lastLogin', 'Never')}")
else:
    print(f"   [X] Could not retrieve user from database")

# Step 7: Test with username instead of email
print("\n7. Testing login with username instead of email...")
username_login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": test_username,  # Use username instead of email
        "password": test_password
    },
    headers={"Content-Type": "application/json"}
)

print(f"   Username login status: {username_login_response.status_code}")
if username_login_response.status_code == 200:
    print(f"   [SUCCESS] Username login works!")
else:
    print(f"   [FAILURE] Username login failed: {username_login_response.text[:100]}")

# Step 8: Cleanup
print("\n8. Cleaning up test user...")
delete_response = requests.delete(
    f"{BASE_URL}/users/{user_id}",
    headers={"Authorization": f"Bearer {admin_token}"}
)
if delete_response.status_code == 200:
    print(f"   [OK] Test user deleted")
else:
    print(f"   Could not delete test user (ID: {user_id})")

print("\n" + "=" * 80)
print("REAL-WORLD SCENARIO TEST COMPLETE")
print("=" * 80)

# Summary
print("\nSUMMARY:")
if login_response.status_code == 200:
    print("✅ Backend authentication is working correctly")
    print("✅ User creation and login flow is successful")
    print("❓ The issue might be in the frontend or a specific edge case")
    print("\nPossible causes:")
    print("1. Frontend not sending correct request format")
    print("2. CORS issues between frontend and backend")
    print("3. Frontend state management issues")
    print("4. Network connectivity issues")
    print("5. Browser-specific issues")
else:
    print("❌ Backend authentication has an issue")
    print(f"   Error: {login_response.text}")
