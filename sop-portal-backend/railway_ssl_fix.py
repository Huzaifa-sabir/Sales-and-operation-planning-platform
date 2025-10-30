#!/usr/bin/env python3
"""
Railway SSL Fix for MongoDB Atlas
This script provides alternative connection methods for Railway deployment
"""
import os
import ssl
from motor.motor_asyncio import AsyncIOMotorClient

def get_railway_mongodb_client():
    """Get MongoDB client configured for Railway deployment"""
    
    # Get connection string from environment
    mongodb_url = os.getenv("MONGODB_URL", "mongodb+srv://huzaifasabir289_db_user:4SLjzoPzm00pQNNv@cluster0.4owv6bf.mongodb.net/sop_portal?retryWrites=true&w=majority")
    
    # Railway-specific SSL configuration
    client = AsyncIOMotorClient(
        mongodb_url,
        tls=True,
        tlsAllowInvalidCertificates=True,
        tlsAllowInvalidHostnames=True,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000,
        retryWrites=True,
        retryReads=True
    )
    
    return client

def test_connection():
    """Test MongoDB connection with Railway configuration"""
    import asyncio
    
    async def test():
        try:
            client = get_railway_mongodb_client()
            await client.admin.command('ping')
            print("✅ Railway MongoDB connection successful!")
            return True
        except Exception as e:
            print(f"❌ Railway MongoDB connection failed: {e}")
            return False
        finally:
            client.close()
    
    return asyncio.run(test())

if __name__ == "__main__":
    print("🧪 Testing Railway MongoDB Atlas Connection")
    print("=" * 50)
    test_connection()

