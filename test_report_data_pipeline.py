"""
Test the report generation data pipeline to find where the issue is
"""
import requests
import json
from pymongo import MongoClient

# MongoDB connection
MONGODB_URI = "mongodb+srv://huzaifasabir289_db_user:4SLjzoPzm00pQNNv@cluster0.4owv6bf.mongodb.net/sop_portal?retryWrites=true&w=majority"
BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("TESTING REPORT GENERATION DATA PIPELINE")
print("=" * 80)

# Connect to MongoDB and test the aggregation pipeline
print("\n1. TESTING MONGODB AGGREGATION PIPELINE...")
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
    db = client.sop_portal
    sales_history = db.sales_history
    
    # Test the exact aggregation pipeline from the report service
    print(f"\n1a. Testing overall totals pipeline...")
    
    # Build match stage (same as report service)
    match_stage = {
        "year": 2024,
        "month": 11
    }
    
    # Overall totals pipeline (from report service)
    totals_pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": None,
                "totalQuantity": {"$sum": "$quantity"},
                "totalRevenue": {"$sum": "$totalSales"},
                "transactionCount": {"$sum": 1},
                "avgQuantity": {"$avg": "$quantity"},
                "avgUnitPrice": {"$avg": "$unitPrice"}
            }
        }
    ]
    
    totals_result = list(sales_history.aggregate(totals_pipeline))
    print(f"   Totals result: {totals_result}")
    
    if totals_result:
        totals = totals_result[0]
        print(f"   Total Quantity: {totals.get('totalQuantity', 0)}")
        print(f"   Total Revenue: ${totals.get('totalRevenue', 0):.2f}")
        print(f"   Transaction Count: {totals.get('transactionCount', 0)}")
        print(f"   Avg Quantity: {totals.get('avgQuantity', 0):.2f}")
        print(f"   Avg Unit Price: ${totals.get('avgUnitPrice', 0):.2f}")
    else:
        print(f"   [WARNING] No totals result!")
    
    # Test monthly trends pipeline
    print(f"\n1b. Testing monthly trends pipeline...")
    monthly_trends_pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": {
                    "year": "$year",
                    "month": "$month"
                },
                "quantity": {"$sum": "$quantity"},
                "revenue": {"$sum": "$totalSales"},
                "transactions": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id.year": 1, "_id.month": 1}
        },
        {"$limit": 24}
    ]
    
    monthly_trends = list(sales_history.aggregate(monthly_trends_pipeline))
    print(f"   Monthly trends result: {monthly_trends}")
    
    # Test top customers pipeline
    print(f"\n1c. Testing top customers pipeline...")
    top_customers_pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": "$customerId",
                "totalRevenue": {"$sum": "$totalSales"},
                "totalQuantity": {"$sum": "$quantity"},
                "transactions": {"$sum": 1}
            }
        },
        {"$sort": {"totalRevenue": -1}},
        {"$limit": 10}
    ]
    
    top_customers = list(sales_history.aggregate(top_customers_pipeline))
    print(f"   Top customers result: {top_customers}")
    
    # Test top products pipeline
    print(f"\n1d. Testing top products pipeline...")
    top_products_pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": "$productId",
                "totalQuantity": {"$sum": "$quantity"},
                "totalRevenue": {"$sum": "$totalSales"},
                "transactions": {"$sum": 1}
            }
        },
        {"$sort": {"totalQuantity": -1}},
        {"$limit": 10}
    ]
    
    top_products = list(sales_history.aggregate(top_products_pipeline))
    print(f"   Top products result: {top_products}")
    
except Exception as e:
    print(f"   [ERROR] MongoDB aggregation test failed: {e}")

# Test the API endpoints
print(f"\n2. TESTING API ENDPOINTS...")
try:
    admin_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@heavygarlic.com", "password": "admin123"},
        headers={"Content-Type": "application/json"}
    )
    
    admin_data = admin_response.json()
    admin_token = admin_data.get("access_token")
    
    # Test sales statistics endpoint
    print(f"\n2a. Testing sales statistics endpoint...")
    stats_response = requests.get(
        f"{BASE_URL}/sales-history/statistics?year=2024&month=11",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    print(f"   Stats status: {stats_response.status_code}")
    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        print(f"   Stats response: {stats_data}")
    else:
        print(f"   Stats error: {stats_response.text[:200]}")
    
    # Test sales by month endpoint
    print(f"\n2b. Testing sales by month endpoint...")
    monthly_response = requests.get(
        f"{BASE_URL}/sales-history/by-month?months=12",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    print(f"   Monthly status: {monthly_response.status_code}")
    if monthly_response.status_code == 200:
        monthly_data = monthly_response.json()
        print(f"   Monthly response: {monthly_data}")
    else:
        print(f"   Monthly error: {monthly_response.text[:200]}")
        
except Exception as e:
    print(f"   [ERROR] API endpoint test failed: {e}")

print(f"\n" + "=" * 80)
print("DATA PIPELINE TEST COMPLETE")
print("=" * 80)
