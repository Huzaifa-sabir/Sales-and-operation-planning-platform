"""
Test script to verify user creation and authentication flow
"""
import asyncio
from app.config.database import db
from app.services.user_service import UserService
from app.models.user import UserCreate, UserRole
from app.utils.security import verify_password

async def test_user_creation_and_login():
    """Test complete user creation and login flow"""

    # Connect to database
    await db.connect_db()
    database = db.get_database()

    user_service = UserService(database)

    # Test user data
    test_email = f"test_auth_{asyncio.get_event_loop().time()}@example.com"
    test_username = f"testuser_{int(asyncio.get_event_loop().time())}"

    print("=" * 60)
    print("TESTING USER CREATION AND AUTHENTICATION FLOW")
    print("=" * 60)

    try:
        # Step 1: Create a new user
        print(f"\n1. Creating user: {test_username}")
        user_create = UserCreate(
            username=test_username,
            email=test_email,
            fullName="Test Auth User",
            role=UserRole.SALES_REP
        )

        created_user, generated_password = await user_service.create_user(user_create)
        print(f"   ✓ User created successfully!")
        print(f"   - User ID: {created_user.id}")
        print(f"   - Username: {created_user.username}")
        print(f"   - Email: {created_user.email}")
        print(f"   - Generated Password: {generated_password}")
        print(f"   - Hashed Password: {created_user.hashedPassword[:50]}...")

        # Step 2: Verify password hashing works
        print(f"\n2. Testing password verification")
        is_valid = verify_password(generated_password, created_user.hashedPassword)
        if is_valid:
            print(f"   ✓ Password verification PASSED - Password matches hash!")
        else:
            print(f"   ✗ Password verification FAILED - Password does NOT match hash!")
            print(f"     This is the problem!")

        # Step 3: Simulate login by finding user and verifying password
        print(f"\n3. Simulating login process")
        user_doc = await database.users.find_one({"email": test_email})
        if user_doc:
            print(f"   ✓ User found in database")
            login_password_matches = verify_password(generated_password, user_doc.get("hashedPassword", ""))
            if login_password_matches:
                print(f"   ✓ LOGIN WOULD SUCCEED - Password matches!")
            else:
                print(f"   ✗ LOGIN WOULD FAIL - Password does NOT match!")
                print(f"     Expected: {generated_password}")
                print(f"     Hash in DB: {user_doc.get('hashedPassword', '')[:50]}...")
        else:
            print(f"   ✗ User NOT found in database!")

        # Step 4: Test with wrong password
        print(f"\n4. Testing with wrong password")
        wrong_password_matches = verify_password("WrongPassword123!", created_user.hashedPassword)
        if wrong_password_matches:
            print(f"   ✗ SECURITY ISSUE - Wrong password matched!")
        else:
            print(f"   ✓ Correct behavior - Wrong password rejected")

        # Clean up - delete test user
        print(f"\n5. Cleaning up test user")
        await database.users.delete_one({"_id": user_doc["_id"]})
        print(f"   ✓ Test user deleted")

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        await db.close_db()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_user_creation_and_login())
