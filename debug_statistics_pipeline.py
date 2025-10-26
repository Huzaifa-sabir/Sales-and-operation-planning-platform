"""
Debug the sales statistics aggregation pipeline
"""
from pymongo import MongoClient

# MongoDB connection
MONGODB_URI = "mongodb+srv://huzaifasabir289_db_user:4SLjzoPzm00pQNNv@cluster0.4owv6bf.mongodb.net/sop_portal?retryWrites=true&w=majority"

print("=" * 80)
print("DEBUGGING SALES STATISTICS AGGREGATION PIPELINE")
print("=" * 80)

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
    db = client.sop_portal
    sales_history = db.sales_history
    
    print("\n1. Testing the exact aggregation pipeline from the service...")
    
    # Build match stage (same as service)
    match_stage = {}
    year = 2024
    month = 11
    
    if year and month:
        # Specific month
        match_stage["year"] = year
        match_stage["month"] = month
    
    print(f"   Match stage: {match_stage}")
    
    # Test the aggregation pipeline (exact copy from service)
    pipeline = []
    
    if match_stage:
        pipeline.append({"$match": match_stage})
    
    pipeline.extend([
        {
            "$group": {
                "_id": None,
                "totalQuantity": {"$sum": "$quantity"},
                "totalRevenue": {"$sum": "$totalSales"},
                "avgQuantity": {"$avg": "$quantity"},
                "avgUnitPrice": {"$avg": "$unitPrice"},
                "recordCount": {"$sum": 1},
                "minQuantity": {"$min": "$quantity"},
                "maxQuantity": {"$max": "$quantity"}
            }
        }
    ])
    
    print(f"   Pipeline: {pipeline}")
    
    result = list(sales_history.aggregate(pipeline))
    print(f"   Result: {result}")
    
    if result:
        stats = result[0]
        print(f"   Processed stats:")
        print(f"     Total Quantity: {stats.get('totalQuantity', 0)}")
        print(f"     Total Revenue: ${stats.get('totalRevenue', 0):.2f}")
        print(f"     Record Count: {stats.get('recordCount', 0)}")
        print(f"     Avg Quantity: {stats.get('avgQuantity', 0):.2f}")
        print(f"     Avg Unit Price: ${stats.get('avgUnitPrice', 0):.2f}")
        
        # Check if this matches our expected values
        expected_revenue = 1004189.55
        expected_quantity = 3920
        expected_count = 7
        
        if abs(stats.get('totalRevenue', 0) - expected_revenue) < 1:
            print(f"   ✅ Revenue is correct!")
        else:
            print(f"   ❌ Revenue is wrong! Expected: ${expected_revenue:.2f}, Got: ${stats.get('totalRevenue', 0):.2f}")
            
        if abs(stats.get('totalQuantity', 0) - expected_quantity) < 1:
            print(f"   ✅ Quantity is correct!")
        else:
            print(f"   ❌ Quantity is wrong! Expected: {expected_quantity}, Got: {stats.get('totalQuantity', 0)}")
            
        if stats.get('recordCount', 0) == expected_count:
            print(f"   ✅ Record count is correct!")
        else:
            print(f"   ❌ Record count is wrong! Expected: {expected_count}, Got: {stats.get('recordCount', 0)}")
    else:
        print(f"   [WARNING] No result from aggregation!")
    
    # Test without match stage to see what happens
    print(f"\n2. Testing without match stage (should return all data)...")
    pipeline_all = [
        {
            "$group": {
                "_id": None,
                "totalQuantity": {"$sum": "$quantity"},
                "totalRevenue": {"$sum": "$totalSales"},
                "avgQuantity": {"$avg": "$quantity"},
                "avgUnitPrice": {"$avg": "$unitPrice"},
                "recordCount": {"$sum": 1},
                "minQuantity": {"$min": "$quantity"},
                "maxQuantity": {"$max": "$quantity"}
            }
        }
    ]
    
    result_all = list(sales_history.aggregate(pipeline_all))
    if result_all:
        stats_all = result_all[0]
        print(f"   All data stats:")
        print(f"     Total Quantity: {stats_all.get('totalQuantity', 0)}")
        print(f"     Total Revenue: ${stats_all.get('totalRevenue', 0):.2f}")
        print(f"     Record Count: {stats_all.get('recordCount', 0)}")
    
    # Test the match stage separately
    print(f"\n3. Testing match stage separately...")
    match_result = list(sales_history.find(match_stage))
    print(f"   Records matching year=2024, month=11: {len(match_result)}")
    
    if match_result:
        print(f"   Sample record:")
        sample = match_result[0]
        print(f"     Year: {sample.get('year')}")
        print(f"     Month: {sample.get('month')}")
        print(f"     Quantity: {sample.get('quantity')}")
        print(f"     Total Sales: ${sample.get('totalSales', 0):.2f}")
    
except Exception as e:
    print(f"   [ERROR] Debug test failed: {e}")

print(f"\n" + "=" * 80)
print("DEBUGGING COMPLETE")
print("=" * 80)
