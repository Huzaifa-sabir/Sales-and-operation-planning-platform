#!/usr/bin/env python3
"""
Test MongoDB Atlas connection with different configurations
"""
import urllib.parse
from pymongo import MongoClient

# Test different connection string formats
def test_connection_strings():
    """Test various connection string formats"""
    
    # Original connection string
    original_url = "mongodb+srv://huzaifasabir289_db_user:4SLjzoPgm00pQNNv@cluster0.4owv6bf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    # URL-encoded password
    password_encoded = urllib.parse.quote("4SLjzoPgm00pQNNv", safe='')
    encoded_url = f"mongodb+srv://huzaifasabir289_db_user:{password_encoded}@cluster0.4owv6bf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    # Without appName
    simple_url = f"mongodb+srv://huzaifasabir289_db_user:{password_encoded}@cluster0.4owv6bf.mongodb.net/sop_portal?retryWrites=true&w=majority"
    
    # Test configurations
    configs = [
        ("Original", original_url),
        ("URL Encoded", encoded_url),
        ("Simple", simple_url)
    ]
    
    for name, url in configs:
        print(f"\n🔍 Testing {name} connection string:")
        print(f"URL: {url}")
        
        try:
            client = MongoClient(url, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            print("✅ Connection successful!")
            
            # Test database access
            db = client['sop_portal']
            collections = db.list_collection_names()
            print(f"📊 Available collections: {collections}")
            
            client.close()
            return url  # Return the working URL
            
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
    
    return None

def test_user_permissions():
    """Test if user has proper permissions"""
    print("\n🔐 Testing user permissions...")
    
    # Try to connect with minimal permissions
    test_url = "mongodb+srv://huzaifasabir289_db_user:4SLjzoPgm00pQNNv@cluster0.4owv6bf.mongodb.net/admin?retryWrites=true&w=majority"
    
    try:
        client = MongoClient(test_url, serverSelectionTimeoutMS=5000)
        
        # Test basic operations
        admin_db = client.admin
        result = admin_db.command('listCollections')
        print("✅ Admin access successful")
        
        # Test database creation
        test_db = client['test_db']
        test_collection = test_db['test_collection']
        test_collection.insert_one({"test": "data"})
        test_collection.delete_many({})
        print("✅ Database write permissions confirmed")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Permission test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 MongoDB Atlas Connection Diagnostic Tool")
    print("=" * 50)
    
    # Test connection strings
    working_url = test_connection_strings()
    
    if working_url:
        print(f"\n🎉 Found working connection string!")
        print(f"Use this URL: {working_url}")
        
        # Test permissions
        test_user_permissions()
        
    else:
        print("\n❌ All connection attempts failed.")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check if password is correct in MongoDB Atlas")
        print("2. Verify user has 'readWrite' permissions")
        print("3. Check Network Access settings (add 0.0.0.0/0)")
        print("4. Ensure database user exists and is active")
        print("5. Try creating a new database user with a simple password")

if __name__ == "__main__":
    main()
