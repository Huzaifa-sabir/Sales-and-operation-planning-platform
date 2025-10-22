#!/usr/bin/env python3
"""
Check admin user details
"""
import asyncio
from app.config.database import db
from app.services.user_service import UserService

async def check_admin():
    try:
        await db.connect_db()
        database = db.get_database()
        user_service = UserService(database)
        
        # Check admin user by username
        admin_user = await user_service.get_user_by_username("admin")
        if admin_user:
            print(f"Admin user found:")
            print(f"- Username: {admin_user.username}")
            print(f"- Email: {admin_user.email}")
            print(f"- Full Name: {admin_user.fullName}")
            print(f"- Role: {admin_user.role}")
            print(f"- Active: {admin_user.isActive}")
        else:
            print("Admin user not found")
            
        await db.close_db()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_admin())
