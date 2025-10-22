#!/usr/bin/env python3
"""
Test authentication flow
"""
import asyncio
from app.config.database import db
from app.utils.auth_dependencies import get_current_user, get_current_active_user, require_admin
from app.utils.jwt import create_access_token
from app.models.user import UserInDB, UserRole

async def test_auth_flow():
    try:
        print("Testing authentication flow...")
        
        # Connect to database
        await db.connect_db()
        database = db.get_database()
        
        # Get admin user
        admin_doc = await database.users.find_one({"email": "admin@heavygarlic.com"})
        
        if admin_doc:
            print(f"✅ Admin user found: {admin_doc.get('username')}")
            
            # Create UserInDB object
            admin_user = UserInDB(
                id=str(admin_doc["_id"]),
                username=admin_doc["username"],
                email=admin_doc["email"],
                fullName=admin_doc.get("fullName", ""),
                role=admin_doc["role"],
                isActive=admin_doc.get("isActive", True),
                hashedPassword=admin_doc.get("hashedPassword", ""),
                loginAttempts=admin_doc.get("loginAttempts", 0),
                lastLogin=admin_doc.get("lastLogin"),
                passwordChangedAt=admin_doc.get("passwordChangedAt"),
                createdAt=admin_doc.get("createdAt"),
                updatedAt=admin_doc.get("updatedAt")
            )
            
            print(f"✅ UserInDB created: {admin_user.username} - {admin_user.role}")
            
            # Test role check
            if admin_user.role == UserRole.ADMIN:
                print("✅ User has admin role")
            else:
                print(f"❌ User does not have admin role: {admin_user.role}")
                
            # Test active check
            if admin_user.isActive:
                print("✅ User is active")
            else:
                print("❌ User is not active")
                
        else:
            print("❌ Admin user not found")
        
        await db.close_db()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
