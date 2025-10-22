#!/usr/bin/env python3
"""
Quick script to check users in the database
"""
import asyncio
from app.config.database import db
from app.services.user_service import UserService
from app.models.user import UserCreate, UserRole

async def check_users():
    try:
        await db.connect_db()
        database = db.get_database()
        user_service = UserService(database)
        
        users = await user_service.list_users(limit=100)
        print(f"Users found: {users['total']}")
        
        for user in users['users']:
            print(f"- {user.username} ({user.role}) - Active: {user.isActive}")
            
        await db.close_db()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_users())
