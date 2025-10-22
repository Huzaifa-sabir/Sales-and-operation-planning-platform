#!/usr/bin/env python3
"""
Test JWT token creation
"""
import asyncio
from app.utils.jwt import create_token_response

def test_jwt():
    try:
        print("Testing JWT token creation...")
        
        # Test creating a token response
        token_response = create_token_response("test_user_id", "test_user", "admin")
        
        print("JWT token creation successful!")
        print(f"Token type: {token_response['token_type']}")
        print(f"Expires in: {token_response['expires_in']} seconds")
        print(f"User: {token_response['user']}")
        print(f"Access token (first 50 chars): {token_response['access_token'][:50]}...")
        
    except Exception as e:
        print(f"JWT creation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_jwt()
