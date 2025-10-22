#!/usr/bin/env python3
"""
Export local MongoDB data to JSON files for backup and migration
"""
import json
import os
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from typing import Dict, List, Any

# Local MongoDB connection
LOCAL_MONGODB_URL = "mongodb://localhost:27017"
LOCAL_DB_NAME = "sop_portal"

# Collections to export
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

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle ObjectId and datetime objects"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def export_collection(collection_name: str, documents: List[Dict]) -> str:
    """Export collection data to JSON file"""
    filename = f"export_{collection_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join("data_export", filename)
    
    # Create export directory if it doesn't exist
    os.makedirs("data_export", exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(documents, f, cls=JSONEncoder, indent=2, ensure_ascii=False)
    
    return filepath

def export_all_data():
    """Export all collections from local MongoDB to JSON files"""
    print("📤 Starting Data Export from Local MongoDB")
    print("=" * 50)
    
    # Connect to local MongoDB
    print("🔌 Connecting to local MongoDB...")
    client = MongoClient(LOCAL_MONGODB_URL)
    try:
        client.admin.command('ping')
        print("✅ Local MongoDB connection successful")
    except Exception as e:
        print(f"❌ Failed to connect to local MongoDB: {e}")
        return
    
    db = client[LOCAL_DB_NAME]
    
    # Export each collection
    total_documents = 0
    exported_files = []
    
    for collection_name in COLLECTIONS:
        print(f"📋 Exporting collection: {collection_name}")
        
        collection = db[collection_name]
        documents = list(collection.find({}))
        
        if documents:
            filepath = export_collection(collection_name, documents)
            exported_files.append(filepath)
            total_documents += len(documents)
            print(f"   ✅ Exported {len(documents)} documents to {filepath}")
        else:
            print(f"   ⚠️  No documents found in {collection_name}")
    
    client.close()
    
    print("=" * 50)
    print(f"🎉 Export completed!")
    print(f"📊 Total documents exported: {total_documents}")
    print(f"📁 Files created: {len(exported_files)}")
    print("\nExported files:")
    for file in exported_files:
        print(f"   - {file}")
    
    return exported_files

def main():
    """Main function"""
    print("MongoDB Data Export Tool")
    print("This will export all data from local MongoDB to JSON files")
    print()
    
    response = input("Do you want to proceed with the export? (y/N): ")
    if response.lower() != 'y':
        print("Export cancelled.")
        return
    
    export_all_data()

if __name__ == "__main__":
    main()
