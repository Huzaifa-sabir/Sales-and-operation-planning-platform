"""
Check if November data exists in MongoDB Atlas
Paste your Render MONGODB_URI when prompted
"""
from pymongo import MongoClient

print("=" * 80)
print("MONGODB ATLAS DATA CHECK")
print("=" * 80)

# Get MongoDB URI
uri = input("\nPaste your Render MONGODB_URI from Render dashboard: ").strip()

if not uri:
    print("ERROR: No URI provided")
    exit(1)

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    db = client['sop_portal']

    # Test connection
    client.server_info()
    print("✓ Connected to MongoDB Atlas\n")

    # Check salesHistory collection
    print("[1] Checking salesHistory collection...")
    total = db.salesHistory.count_documents({})
    print(f"    Total records: {total}")

    # Check November 2025
    nov_count = db.salesHistory.count_documents({"year": 2025, "monthNum": 11})
    print(f"    November 2025: {nov_count} records")

    # Check October 2025
    oct_count = db.salesHistory.count_documents({"year": 2025, "monthNum": 10})
    print(f"    October 2025: {oct_count} records")

    # Show a sample November record
    if nov_count > 0:
        print("\n[2] Sample November 2025 record:")
        sample = db.salesHistory.find_one({"year": 2025, "monthNum": 11})
        print(f"    Customer: {sample.get('customerName')}")
        print(f"    Product: {sample.get('productDescription')}")
        print(f"    Quantity: {sample.get('quantity')}")
        print(f"    Unit Price: ${sample.get('unitPrice')}")
        print(f"    Total Sales: ${sample.get('totalSales')}")
        print(f"    Month field: {sample.get('month')} (string)")
        print(f"    MonthNum field: {sample.get('monthNum')} (integer)")
    else:
        print("\n[2] NO November 2025 data found!")
        print("    This is why reports show $0.00")

        # Check if October has data
        if oct_count > 0:
            print("\n    But October 2025 HAS data:")
            sample_oct = db.salesHistory.find_one({"year": 2025, "monthNum": 10})
            print(f"    Customer: {sample_oct.get('customerName')}")
            print(f"    Product: {sample_oct.get('productDescription')}")
            print(f"    Total Sales: ${sample_oct.get('totalSales')}")

    # Calculate November totals if data exists
    if nov_count > 0:
        print("\n[3] November 2025 Totals:")
        pipeline = [
            {"$match": {"year": 2025, "monthNum": 11}},
            {"$group": {
                "_id": None,
                "totalRevenue": {"$sum": "$totalSales"},
                "totalQuantity": {"$sum": "$quantity"},
                "count": {"$sum": 1}
            }}
        ]
        result = list(db.salesHistory.aggregate(pipeline))
        if result:
            totals = result[0]
            print(f"    Total Revenue: ${totals['totalRevenue']:,.2f}")
            print(f"    Total Quantity: {totals['totalQuantity']:,.2f}")
            print(f"    Transaction Count: {totals['count']}")

            print("\n✓ Data EXISTS - backend should return this data!")
            print("  If report shows $0.00, backend code has a bug")

    client.close()

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print("\nPossible issues:")
    print("1. Wrong MongoDB URI")
    print("2. IP not whitelisted in Atlas")
    print("3. Network connection issue")

print("\n" + "=" * 80)
