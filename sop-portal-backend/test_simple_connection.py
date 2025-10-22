#!/usr/bin/env python3
"""
Simple MongoDB Atlas connection test
"""
from pymongo import MongoClient

def test_connection():
    """Test MongoDB Atlas connection with simple credentials"""
    
    # Try with a simple test user (you'll need to create this)
    test_urls = [
        # Option 1: Try with your existing user but different format
        "mongodb+srv://huzaifasabir289_db_user:4SLjzoPzm00pQNNv@cluster0.4owv6bf.mongodb.net/sop_portal",
        
        # Option 2: Try without database name
        "mongodb+srv://huzaifasabir289_db_user:4SLjzoPzm00pQNNv@cluster0.4owv6bf.mongodb.net/",
        
        # Option 3: Try with admin database
        "mongodb+srv://huzaifasabir289_db_user:4SLjzoPzm00pQNNv@cluster0.4owv6bf.mongodb.net/admin"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🔍 Test {i}: {url}")
        try:
            client = MongoClient(url, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            print("✅ Connection successful!")
            
            # List databases
            databases = client.list_database_names()
            print(f"📊 Available databases: {databases}")
            
            client.close()
            return url
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
    
    return None

if __name__ == "__main__":
    print("🧪 Simple MongoDB Atlas Connection Test")
    print("=" * 40)
    
    working_url = test_connection()
    
    if working_url:
        print(f"\n🎉 Working connection string found!")
        print(f"Use: {working_url}")
    else:
        print("\n❌ All connection attempts failed.")
        print("\nNext steps:")
        print("1. Create a new database user in MongoDB Atlas")
        print("2. Use a simple password (no special characters)")
        print("3. Ensure Network Access allows 0.0.0.0/0")
        print("4. Check the create_atlas_user_guide.md file")
