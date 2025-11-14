"""
Update Admin Credentials Script
Updates admin user to: lpolo@garlandfood.net / admin123
"""
import asyncio
import os
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except ImportError:
    print("Error: passlib not installed. Install with: pip install passlib[bcrypt]")
    sys.exit(1)


async def update_admin_credentials():
    """Update admin user to lpolo@garlandfood.net with password admin123"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get MongoDB URL from environment
    mongodb_url = os.getenv('MONGODB_URL')
    if not mongodb_url:
        print("Error: MONGODB_URL not found in environment")
        print("Please set MONGODB_URL in your .env file")
        return
    
    # Extract database name from URL
    db_name = "sop_portal"
    if "/" in mongodb_url:
        parts = mongodb_url.split("/")
        if len(parts) > 3:
            db_part = parts[-1].split("?")[0]
            if db_part:
                db_name = db_part
    
    client = AsyncIOMotorClient(mongodb_url)
    db = client[db_name]
    users_collection = db.users
    
    print("=" * 60)
    print("Updating Admin Credentials")
    print("=" * 60)
    
    # Check if new admin user already exists
    new_admin = await users_collection.find_one({"email": "lpolo@garlandfood.net"})
    old_admin = await users_collection.find_one({"email": "admin@heavygarlic.com"})
    
    # Generate password hash for admin123
    password_hash = pwd_context.hash("admin123")
    
    if new_admin:
        # Update existing lpolo@garlandfood.net user
        print(f"Found existing user: lpolo@garlandfood.net")
        print(f"Updating password and ensuring admin role...")
        
        update_result = await users_collection.update_one(
            {"email": "lpolo@garlandfood.net"},
            {
                "$set": {
                    "passwordHash": password_hash,
                    "hashedPassword": password_hash,  # Support both field names
                    "role": "admin",
                    "isActive": True,
                    "username": "lpolo",
                    "fullName": "L Polo",
                    "updatedAt": datetime.now(timezone.utc)
                }
            }
        )
        
        if update_result.modified_count > 0:
            print(f"✅ Successfully updated lpolo@garlandfood.net")
        else:
            print(f"⚠️  User already has correct credentials")
    else:
        # Create new admin user
        print(f"Creating new admin user: lpolo@garlandfood.net")
        
        user_doc = {
            "username": "lpolo",
            "email": "lpolo@garlandfood.net",
            "passwordHash": password_hash,
            "hashedPassword": password_hash,  # Support both field names
            "fullName": "L Polo",
            "role": "admin",
            "isActive": True,
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
            "lastLogin": None,
            "loginAttempts": 0
        }
        
        result = await users_collection.insert_one(user_doc)
        print(f"✅ Successfully created lpolo@garlandfood.net (ID: {result.inserted_id})")
    
    # Deactivate old admin user if it exists and is different
    if old_admin and old_admin.get("email") != "lpolo@garlandfood.net":
        print(f"\nFound old admin user: admin@heavygarlic.com")
        print(f"Deactivating old admin user...")
        
        # Deactivate old admin (don't change email/username to avoid duplicate key error)
        await users_collection.update_one(
            {"email": "admin@heavygarlic.com"},
            {
                "$set": {
                    "isActive": False,
                    "updatedAt": datetime.now(timezone.utc)
                }
            }
        )
        print(f"✅ Deactivated admin@heavygarlic.com")
    
    # Verify the update
    verify_user = await users_collection.find_one({"email": "lpolo@garlandfood.net"})
    if verify_user:
        # Test password verification
        stored_hash = verify_user.get("passwordHash") or verify_user.get("hashedPassword")
        if stored_hash:
            test_verify = pwd_context.verify("admin123", stored_hash)
            print("\n" + "=" * 60)
            print("Verification Results")
            print("=" * 60)
            print(f"Email: {verify_user.get('email')}")
            print(f"Username: {verify_user.get('username')}")
            print(f"Role: {verify_user.get('role')}")
            print(f"Is Active: {verify_user.get('isActive')}")
            print(f"Password Verification: {'✅ PASS' if test_verify else '❌ FAIL'}")
            print("=" * 60)
            print("\n✅ Admin credentials updated successfully!")
            print(f"   Email: lpolo@garlandfood.net")
            print(f"   Password: admin123")
            print("=" * 60)
        else:
            print("❌ Error: Password hash not found in user document")
    else:
        print("❌ Error: Could not verify updated user")
    
    client.close()


if __name__ == '__main__':
    asyncio.run(update_admin_credentials())

