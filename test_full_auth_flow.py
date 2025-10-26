"""
Complete authentication flow test
"""
import requests
import json

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 70)
print("TESTING COMPLETE USER CREATION AND LOGIN FLOW")
print("=" * 70)

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
print(f"   Token: {admin_token[:30]}...")

# Step 2: Create a new user with a known password
print("\n2. Creating test user...")
import time
timestamp = int(time.time())
test_username = f"pytest_{timestamp}"
test_email = f"pytest_{timestamp}@test.com"
test_password = "PyTestPass123!"

create_response = requests.post(
    f"{BASE_URL}/users",
    json={
        "username": test_username,
        "email": test_email,
        "fullName": "Python Test User",
        "role": "sales_rep",
        "password": test_password
    },
    headers={
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
)

if create_response.status_code != 201:
    print(f"   [X] User creation failed: {create_response.status_code}")
    print(f"   Response: {create_response.text}")
    exit(1)

create_data = create_response.json()
print(f"   [OK] User created successfully")
print(f"   Username: {create_data['user']['username']}")
print(f"   Email: {create_data['user']['email']}")
print(f"   Returned password: {create_data.get('generatedPassword', 'NOT RETURNED')}")

# Step 3: Try to login with the created user
print("\n3. Testing login with created user...")
print(f"   Attempting login with:")
print(f"   - Email: {test_email}")
print(f"   - Password: {test_password}")

login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": test_email, "password": test_password},
    headers={"Content-Type": "application/json"}
)

print(f"\n   Login response status: {login_response.status_code}")
print(f"   Login response: {login_response.text[:200]}")

if login_response.status_code == 200:
    login_data = login_response.json()
    print(f"\n   [OK][OK][OK] LOGIN SUCCESSFUL! [OK][OK][OK]")
    print(f"   Logged in as: {login_data['user']['username']}")
    print(f"   Token: {login_data['access_token'][:30]}...")
else:
    print(f"\n   [X][X][X] LOGIN FAILED! [X][X][X]")
    print(f"   This means the password is NOT being used correctly")

# Step 4: Cleanup - delete test user
print("\n4. Cleaning up test user...")
user_id = create_data['user']['_id']
delete_response = requests.delete(
    f"{BASE_URL}/users/{user_id}",
    headers={"Authorization": f"Bearer {admin_token}"}
)
if delete_response.status_code == 200:
    print(f"   [OK] Test user deleted")
else:
    print(f"   Could not delete test user (ID: {user_id})")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
