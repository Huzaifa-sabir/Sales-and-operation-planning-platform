"""
Create Admin User Script
Creates admin user: lpolo@garlandfood.net
"""
import asyncio
import os
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except ImportError:
    print("Error: passlib not installed. Install with: pip install passlib[bcrypt]")
    sys.exit(1)


async def create_admin_user():
    """Create admin user lpolo@garlandfood.net"""
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
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": "lpolo@garlandfood.net"})
    
    if existing_user:
        print("=" * 50)
        print("User lpolo@garlandfood.net already exists!")
        print("=" * 50)
        print(f"User ID: {existing_user['_id']}")
        print(f"Username: {existing_user.get('username', 'N/A')}")
        print(f"Role: {existing_user.get('role', 'N/A')}")
        print(f"Is Active: {existing_user.get('isActive', False)}")
        print("=" * 50)
        client.close()
        return
    
    # Generate password hash
    # Default password: Admin123! (change this after first login)
    password_hash = pwd_context.hash("Admin123!")
    
    # Create user document
    user_doc = {
        "username": "lpolo",
        "email": "lpolo@garlandfood.net",
        "passwordHash": password_hash,
        "fullName": "L Polo",
        "role": "admin",
        "isActive": True,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
        "lastLogin": None
    }
    
    # Insert user
    result = await users_collection.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    print("=" * 50)
    print("Admin User Created Successfully!")
    print("=" * 50)
    print(f"User ID: {user_id}")
    print(f"Email: lpolo@garlandfood.net")
    print(f"Username: lpolo")
    print(f"Password: Admin123!")
    print(f"Role: admin")
    print("=" * 50)
    print("IMPORTANT: Please change the password after first login!")
    print("=" * 50)
    
    client.close()


if __name__ == '__main__':
    asyncio.run(create_admin_user())

