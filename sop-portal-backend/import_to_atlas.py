#!/usr/bin/env python3
"""
Import data from JSON files to MongoDB Atlas
"""
import json
import os
import glob
from datetime import datetime
from pymongo import MongoClient
from typing import Dict, List, Any

# MongoDB Atlas connection
ATLAS_MONGODB_URL = "mongodb+srv://huzaifasabir289_db_user:4SLjzoPzm00pQNNv@cluster0.4owv6bf.mongodb.net/sop_portal?retryWrites=true&w=majority"
ATLAS_DB_NAME = "sop_portal"

def import_json_file(filepath: str, collection_name: str):
    """Import data from JSON file to Atlas collection"""
    print(f"📥 Importing {filepath} to {collection_name}")
    
    # Connect to Atlas
    client = MongoClient(ATLAS_MONGODB_URL)
    try:
        client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB Atlas: {e}")
        return
    
    db = client[ATLAS_DB_NAME]
    collection = db[collection_name]
    
    # Load JSON data
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        print(f"   ⚠️  No data in {filepath}")
        return
    
    # Clear existing data (optional)
    existing_count = collection.count_documents({})
    if existing_count > 0:
        print(f"   🗑️  Clearing {existing_count} existing documents")
        collection.delete_many({})
    
    # Insert data
    try:
        if isinstance(data, list):
            result = collection.insert_many(data)
            print(f"   ✅ Imported {len(result.inserted_ids)} documents")
        else:
            result = collection.insert_one(data)
            print(f"   ✅ Imported 1 document")
        
        # Verify import
        final_count = collection.count_documents({})
        print(f"   📊 Total documents in {collection_name}: {final_count}")
        
    except Exception as e:
        print(f"   ❌ Error importing to {collection_name}: {str(e)}")
    
    client.close()

def import_all_data():
    """Import all JSON files to MongoDB Atlas"""
    print("📥 Starting Data Import to MongoDB Atlas")
    print("=" * 50)
    
    # Check if password is set
    if "<db_password>" in ATLAS_MONGODB_URL:
        print("❌ Please replace <db_password> in the ATLAS_MONGODB_URL with your actual password")
        print("   Edit the script and update the connection string")
        return
    
    # Find all export files
    export_dir = "data_export"
    if not os.path.exists(export_dir):
        print(f"❌ Export directory '{export_dir}' not found")
        print("   Please run export_local_data.py first")
        return
    
    # Get all JSON files
    json_files = glob.glob(os.path.join(export_dir, "export_*.json"))
    
    if not json_files:
        print(f"❌ No export files found in '{export_dir}'")
        return
    
    print(f"📁 Found {len(json_files)} export files")
    
    # Import each file
    for filepath in json_files:
        filename = os.path.basename(filepath)
        
        # Extract collection name from filename
        # Format: export_collectionname_timestamp.json
        parts = filename.replace('.json', '').split('_')
        if len(parts) >= 2:
            collection_name = '_'.join(parts[1:-1])  # Skip 'export' and timestamp
        else:
            print(f"   ⚠️  Could not determine collection name for {filename}")
            continue
        
        import_json_file(filepath, collection_name)
        print("-" * 30)
    
    print("🎉 Import completed!")

def main():
    """Main function"""
    print("MongoDB Atlas Import Tool")
    print("This will import all JSON files to MongoDB Atlas")
    print()
    
    response = input("Do you want to proceed with the import? (y/N): ")
    if response.lower() != 'y':
        print("Import cancelled.")
        return
    
    import_all_data()

if __name__ == "__main__":
    main()
