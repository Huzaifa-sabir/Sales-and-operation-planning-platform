"""
Debug the sales history service data conversion issue
"""
import requests
import json
from pymongo import MongoClient

# MongoDB connection
MONGODB_URI = "mongodb+srv://huzaifasabir289_db_user:4SLjzoPzm00pQNNv@cluster0.4owv6bf.mongodb.net/sop_portal?retryWrites=true&w=majority"
BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("DEBUGGING SALES HISTORY DATA CONVERSION")
print("=" * 80)

# Connect to MongoDB and examine raw data
print("\n1. EXAMINING RAW DATABASE DATA...")
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
    db = client.sop_portal
    sales_history = db.sales_history
    
    # Get a sample record
    sample_record = sales_history.find_one({"year": 2024, "month": 11})
    if sample_record:
        print(f"   Sample record structure:")
        for key, value in sample_record.items():
            print(f"     {key}: {type(value).__name__} = {value}")
        
        # Test the conversion logic
        print(f"\n2. TESTING CONVERSION LOGIC...")
        record = sample_record.copy()
        record["_id"] = str(record["_id"])
        
        # This is what the service is trying to do
        converted_record = {
            "id": record["_id"],
            "customerId": record.get("customerId", ""),
            "customerName": record.get("customerName", ""),
            "productId": record.get("productId", ""),
            "productCode": record.get("productCode", ""),
            "productDescription": record.get("productDescription", ""),
            "yearMonth": record.get("yearMonth", ""),
            "year": record.get("year", 0),
            "month": record.get("month", 0),
            "quantity": record.get("quantity", 0),
            "unitPrice": record.get("unitPrice", 0),
            "totalSales": record.get("totalSales", 0),
            "costPrice": record.get("costPrice"),
            "cogs": record.get("cogs"),
            "grossProfit": record.get("grossProfit"),
            "grossProfitPercent": record.get("grossProfitPercent"),
            "salesRepId": record.get("salesRepId", ""),
            "salesRepName": record.get("salesRepName", ""),
            "createdAt": record.get("createdAt")
        }
        
        print(f"   Converted record:")
        for key, value in converted_record.items():
            print(f"     {key}: {type(value).__name__} = {value}")
            
    else:
        print(f"   [ERROR] No sample record found!")
        
except Exception as e:
    print(f"   [ERROR] Database connection failed: {e}")

# Test the API with a simple query
print(f"\n3. TESTING API WITH SIMPLE QUERY...")
try:
    admin_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@heavygarlic.com", "password": "admin123"},
        headers={"Content-Type": "application/json"}
    )
    
    admin_data = admin_response.json()
    admin_token = admin_data.get("access_token")
    
    # Test with minimal parameters
    response = requests.get(
        f"{BASE_URL}/sales-history?limit=1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    print(f"   API Response Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Response structure: {list(data.keys())}")
        print(f"   Total records: {data.get('total', 0)}")
        print(f"   Records array length: {len(data.get('records', []))}")
        
        if data.get('records'):
            print(f"   First record:")
            first_record = data['records'][0]
            for key, value in first_record.items():
                print(f"     {key}: {type(value).__name__} = {value}")
        else:
            print(f"   [WARNING] No records in response!")
            
            # Let's check if there's an error in the response
            print(f"   Full response: {json.dumps(data, indent=2, default=str)}")
    else:
        print(f"   [ERROR] API request failed: {response.text}")
        
except Exception as e:
    print(f"   [ERROR] API test failed: {e}")

print(f"\n" + "=" * 80)
print("DEBUGGING COMPLETE")
print("=" * 80)
