#!/usr/bin/env python3
"""
Test the complete login flow step by step
"""
import asyncio
from app.config.database import db
from app.utils.security import verify_password
from app.utils.jwt import create_token_response

async def test_login_flow():
    try:
        print("Testing complete login flow...")
        
        # Connect to database
        await db.connect_db()
        database = db.get_database()
        
        # Test credentials
        email = "admin@heavygarlic.com"
        password = "admin123"
        
        print(f"Looking for user with email: {email}")
        
        # Find user by email
        user_doc = await database.users.find_one({"email": email})
        
        if not user_doc:
            print("User not found by email, trying username...")
            user_doc = await database.users.find_one({"username": "admin"})
        
        if not user_doc:
            print("User not found!")
            return
        
        print(f"User found: {user_doc.get('username')}")
        print(f"Email: {user_doc.get('email')}")
        print(f"Role: {user_doc.get('role')}")
        print(f"Is Active: {user_doc.get('isActive')}")
        print(f"Login Attempts: {user_doc.get('loginAttempts', 0)}")
        
        # Check if account is locked
        login_attempts = user_doc.get("loginAttempts", 0)
        print(f"Login attempts: {login_attempts}")
        
        # Check if user is active
        if not user_doc.get("isActive", False):
            print("Account is inactive!")
            return
        
        print("Account is active, checking password...")
        
        # Verify password
        hashed_password = user_doc.get("hashedPassword", "")
        print(f"Has hashed password: {bool(hashed_password)}")
        
        if not verify_password(password, hashed_password):
            print("Password verification failed!")
            return
        
        print("Password verification successful!")
        
        # Create token
        user_id = str(user_doc["_id"])
        username = user_doc["username"]
        role = user_doc["role"]
        
        print(f"Creating token for user_id: {user_id}, username: {username}, role: {role}")
        
        token_response = create_token_response(user_id, username, role)
        
        print("Token creation successful!")
        print(f"Token type: {token_response['token_type']}")
        print(f"User: {token_response['user']}")
        
        await db.close_db()
        
    except Exception as e:
        print(f"Error in login flow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_login_flow())
