#!/usr/bin/env python3
"""
Migration script to move data from local MongoDB to MongoDB Atlas
"""
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import json
from datetime import datetime
from typing import Dict, List, Any

# Local MongoDB connection
LOCAL_MONGODB_URL = "mongodb://localhost:27017"
LOCAL_DB_NAME = "sop_portal"

# MongoDB Atlas connection
ATLAS_MONGODB_URL = "mongodb+srv://huzaifasabir289_db_user:4SLjzoPgm00pQNNv@cluster0.4owv6bf.mongodb.net/sop_portal?retryWrites=true&w=majority"
ATLAS_DB_NAME = "sop_portal"

# Collections to migrate
COLLECTIONS = [
    "users",
    "customers", 
    "products",
    "sop_cycles",
    "forecasts",
    "sales_history",
    "reports",
    "settings",
    "audit_logs",
    "product_customer_matrix"
]

async def migrate_collection(local_client, atlas_client, collection_name: str):
    """Migrate a single collection from local to Atlas"""
    print(f"🔄 Migrating collection: {collection_name}")
    
    local_db = local_client[LOCAL_DB_NAME]
    atlas_db = atlas_client[ATLAS_DB_NAME]
    
    local_collection = local_db[collection_name]
    atlas_collection = atlas_db[collection_name]
    
    # Count documents in local collection
    local_count = local_collection.count_documents({})
    print(f"   📊 Local documents: {local_count}")
    
    if local_count == 0:
        print(f"   ⚠️  No documents to migrate in {collection_name}")
        return
    
    # Get all documents from local
    documents = list(local_collection.find({}))
    
    if not documents:
        print(f"   ⚠️  No documents found in {collection_name}")
        return
    
    # Clear existing data in Atlas (optional)
    atlas_count_before = atlas_collection.count_documents({})
    if atlas_count_before > 0:
        print(f"   🗑️  Clearing {atlas_count_before} existing documents in Atlas")
        atlas_collection.delete_many({})
    
    # Insert documents into Atlas
    try:
        result = atlas_collection.insert_many(documents)
        atlas_count_after = atlas_collection.count_documents({})
        print(f"   ✅ Successfully migrated {len(result.inserted_ids)} documents")
        print(f"   📊 Atlas documents after: {atlas_count_after}")
    except Exception as e:
        print(f"   ❌ Error migrating {collection_name}: {str(e)}")

async def migrate_all_data():
    """Migrate all collections from local MongoDB to Atlas"""
    print("🚀 Starting MongoDB Atlas Migration")
    print("=" * 50)
    
    # Connect to local MongoDB
    print("🔌 Connecting to local MongoDB...")
    local_client = MongoClient(LOCAL_MONGODB_URL)
    try:
        local_client.admin.command('ping')
        print("✅ Local MongoDB connection successful")
    except Exception as e:
        print(f"❌ Failed to connect to local MongoDB: {e}")
        return
    
    # Connect to MongoDB Atlas
    print("🔌 Connecting to MongoDB Atlas...")
    atlas_client = MongoClient(ATLAS_MONGODB_URL)
    try:
        atlas_client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB Atlas: {e}")
        return
    
    # Migrate each collection
    for collection_name in COLLECTIONS:
        try:
            await migrate_collection(local_client, atlas_client, collection_name)
        except Exception as e:
            print(f"❌ Error migrating {collection_name}: {str(e)}")
        print("-" * 30)
    
    # Close connections
    local_client.close()
    atlas_client.close()
    
    print("🎉 Migration completed!")
    print("=" * 50)

def main():
    """Main function"""
    print("MongoDB Atlas Migration Tool")
    print("This will migrate all data from local MongoDB to MongoDB Atlas")
    print()
    
    # Check if password is set
    if "<db_password>" in ATLAS_MONGODB_URL:
        print("❌ Please replace <db_password> in the ATLAS_MONGODB_URL with your actual password")
        print("   Edit the script and update the connection string")
        return
    
    # Confirm migration
    response = input("Do you want to proceed with the migration? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    # Run migration
    asyncio.run(migrate_all_data())

if __name__ == "__main__":
    main()
