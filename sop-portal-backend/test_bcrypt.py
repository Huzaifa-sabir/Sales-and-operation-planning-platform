"""
Simple test to verify bcrypt is working correctly
"""
import bcrypt

def test_bcrypt():
    """Test bcrypt hashing and verification"""

    print("=" * 60)
    print("TESTING BCRYPT PASSWORD HASHING")
    print("=" * 60)

    # Test password
    test_password = "TestPassword123!"

    print(f"\n1. Original password: {test_password}")

    # Hash it
    password_bytes = test_password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    hashed_str = hashed.decode('utf-8')

    print(f"2. Hashed password: {hashed_str}")
    print(f"3. Hash length: {len(hashed_str)}")

    # Verify correct password
    is_valid = bcrypt.checkpw(password_bytes, hashed)
    print(f"\n4. Verify CORRECT password: {is_valid}")

    # Verify wrong password
    wrong_password = "WrongPassword123!"
    wrong_bytes = wrong_password.encode('utf-8')[:72]
    is_invalid = bcrypt.checkpw(wrong_bytes, hashed)
    print(f"5. Verify WRONG password: {is_invalid}")

    # Test with extra spaces (common copy/paste issue)
    password_with_spaces = f" {test_password} "
    spaces_bytes = password_with_spaces.encode('utf-8')[:72]
    with_spaces = bcrypt.checkpw(spaces_bytes, hashed)
    print(f"\n6. Password with spaces ' {test_password} ': {with_spaces}")

    # Test case sensitivity
    upper_password = test_password.upper()
    upper_bytes = upper_password.encode('utf-8')[:72]
    is_upper = bcrypt.checkpw(upper_bytes, hashed)
    print(f"7. Upper case password: {is_upper}")

    print("\n" + "=" * 60)
    print("If all tests passed, bcrypt is working correctly!")
    print("=" * 60)

if __name__ == "__main__":
    test_bcrypt()
