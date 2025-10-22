#!/usr/bin/env python3
"""
Check admin user in database
"""
import asyncio
from app.config.database import db

async def check_admin_user():
    try:
        print("Checking admin user in database...")
        
        # Connect to database
        await db.connect_db()
        database = db.get_database()
        
        # Check admin user
        admin_user = await database.users.find_one({"email": "admin@heavygarlic.com"})
        
        if admin_user:
            print(f"✅ Admin user found:")
            print(f"  Username: {admin_user.get('username')}")
            print(f"  Email: {admin_user.get('email')}")
            print(f"  Role: {admin_user.get('role')}")
            print(f"  IsActive: {admin_user.get('isActive')}")
        else:
            print("❌ Admin user not found")
        
        await db.close_db()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_admin_user())
