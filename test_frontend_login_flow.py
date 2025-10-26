"""
Test the exact frontend login flow to identify the issue
"""
import requests
import json
import time

BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("TESTING FRONTEND LOGIN FLOW - EXACT REPLICATION")
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
print(f"   Token: {admin_token[:30]}...")

# Step 2: Create a new user with a specific password
print("\n2. Creating test user with specific password...")
timestamp = int(time.time())
test_username = f"frontend_test_{timestamp}"
test_email = f"frontend_test_{timestamp}@test.com"
test_password = "FrontendTest123!"

create_response = requests.post(
    f"{BASE_URL}/users",
    json={
        "username": test_username,
        "email": test_email,
        "fullName": "Frontend Test User",
        "role": "sales_rep",
        "password": test_password  # Explicitly set password
    },
    headers={
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
)

print(f"   Create response status: {create_response.status_code}")
print(f"   Create response: {create_response.text[:300]}")

if create_response.status_code != 201:
    print(f"   [X] User creation failed")
    exit(1)

create_data = create_response.json()
print(f"   [OK] User created successfully")
print(f"   Username: {create_data['user']['username']}")
print(f"   Email: {create_data['user']['email']}")
print(f"   Generated password: {create_data.get('generatedPassword', 'NOT RETURNED')}")

# Step 3: Test login with the created user - EXACT frontend format
print("\n3. Testing login with created user (frontend format)...")
print(f"   Attempting login with:")
print(f"   - Email: {test_email}")
print(f"   - Password: {test_password}")

# This is the EXACT format the frontend sends
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": test_email,  # Frontend sends as 'email'
        "password": test_password
    },
    headers={"Content-Type": "application/json"}
)

print(f"\n   Login response status: {login_response.status_code}")
print(f"   Login response headers: {dict(login_response.headers)}")
print(f"   Login response body: {login_response.text[:500]}")

if login_response.status_code == 200:
    login_data = login_response.json()
    print(f"\n   [OK][OK][OK] LOGIN SUCCESSFUL! [OK][OK][OK]")
    print(f"   Logged in as: {login_data['user']['username']}")
    print(f"   Token: {login_data['access_token'][:30]}...")
else:
    print(f"\n   [X][X][X] LOGIN FAILED! [X][X][X]")
    print(f"   Status: {login_response.status_code}")
    print(f"   Response: {login_response.text}")

# Step 4: Test with different login formats
print("\n4. Testing alternative login formats...")

# Test with username instead of email
print("\n4a. Testing with username field...")
login_response_username = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": test_email,  # Try username field with email
        "password": test_password
    },
    headers={"Content-Type": "application/json"}
)

print(f"   Username login status: {login_response_username.status_code}")
print(f"   Username login response: {login_response_username.text[:200]}")

# Test with actual username
print("\n4b. Testing with actual username...")
login_response_actual_username = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": test_username,  # Use actual username
        "password": test_password
    },
    headers={"Content-Type": "application/json"}
)

print(f"   Actual username login status: {login_response_actual_username.status_code}")
print(f"   Actual username login response: {login_response_actual_username.text[:200]}")

# Step 5: Check user in database
print("\n5. Checking user in database...")
user_id = create_data['user']['_id']
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
else:
    print(f"   [X] Could not retrieve user from database")

# Step 6: Cleanup - delete test user
print("\n6. Cleaning up test user...")
delete_response = requests.delete(
    f"{BASE_URL}/users/{user_id}",
    headers={"Authorization": f"Bearer {admin_token}"}
)
if delete_response.status_code == 200:
    print(f"   [OK] Test user deleted")
else:
    print(f"   Could not delete test user (ID: {user_id})")

print("\n" + "=" * 80)
print("FRONTEND LOGIN FLOW TEST COMPLETE")
print("=" * 80)
