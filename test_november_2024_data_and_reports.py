"""
Comprehensive test to check November 2024 data and report generation
"""
import requests
import json
from pymongo import MongoClient
from datetime import datetime
import pandas as pd

# MongoDB connection
MONGODB_URI = "mongodb+srv://huzaifasabir289_db_user:4SLjzoPzm00pQNNv@cluster0.4owv6bf.mongodb.net/sop_portal?retryWrites=true&w=majority"
BASE_URL = "https://sales-and-operation-planning-platform-1.onrender.com/api/v1"

print("=" * 80)
print("COMPREHENSIVE NOVEMBER 2024 DATA AND REPORT ANALYSIS")
print("=" * 80)

# Step 1: Connect to MongoDB and check data
print("\n1. CONNECTING TO MONGODB AND CHECKING DATA...")
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
    db = client.sop_portal
    
    print(f"   [OK] Connected to MongoDB")
    print(f"   Database: {db.name}")
    
    # Check collections
    collections = db.list_collection_names()
    print(f"   Collections: {collections}")
    
    # Check sales history for November 2024
    print(f"\n1a. CHECKING SALES HISTORY FOR NOVEMBER 2024...")
    sales_history = db.sales_history
    
    # Query for November 2024 data
    nov_2024_query = {
        "year": 2024,
        "month": 11
    }
    
    nov_2024_count = sales_history.count_documents(nov_2024_query)
    print(f"   November 2024 sales records: {nov_2024_count}")
    
    if nov_2024_count > 0:
        # Get sample records
        sample_records = list(sales_history.find(nov_2024_query).limit(5))
        print(f"   Sample November 2024 records:")
        for i, record in enumerate(sample_records):
            print(f"     {i+1}. Customer: {record.get('customerName', 'N/A')}")
            print(f"        Product: {record.get('productDescription', 'N/A')}")
            print(f"        Quantity: {record.get('quantity', 0)}")
            print(f"        Total Sales: ${record.get('totalSales', 0):.2f}")
            print(f"        Year-Month: {record.get('yearMonth', 'N/A')}")
            print()
        
        # Calculate totals for November 2024
        pipeline = [
            {"$match": nov_2024_query},
            {"$group": {
                "_id": None,
                "totalQuantity": {"$sum": "$quantity"},
                "totalSales": {"$sum": "$totalSales"},
                "recordCount": {"$sum": 1}
            }}
        ]
        
        totals = list(sales_history.aggregate(pipeline))
        if totals:
            total_data = totals[0]
            print(f"   November 2024 Totals:")
            print(f"     Total Quantity: {total_data['totalQuantity']}")
            print(f"     Total Sales: ${total_data['totalSales']:.2f}")
            print(f"     Record Count: {total_data['recordCount']}")
    else:
        print(f"   [WARNING] No November 2024 sales data found!")
        
        # Check what months we do have
        print(f"\n1b. CHECKING AVAILABLE MONTHS IN SALES HISTORY...")
        pipeline = [
            {"$group": {
                "_id": {"year": "$year", "month": "$month"},
                "count": {"$sum": 1},
                "totalSales": {"$sum": "$totalSales"}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        
        available_months = list(sales_history.aggregate(pipeline))
        print(f"   Available months in database:")
        for month_data in available_months:
            year = month_data['_id']['year']
            month = month_data['_id']['month']
            count = month_data['count']
            total_sales = month_data['totalSales']
            print(f"     {year}-{month:02d}: {count} records, ${total_sales:.2f}")
    
    # Check cycles
    print(f"\n1c. CHECKING S&OP CYCLES...")
    cycles = db.sop_cycles
    cycles_count = cycles.count_documents({})
    print(f"   Total cycles: {cycles_count}")
    
    if cycles_count > 0:
        sample_cycles = list(cycles.find().limit(3))
        for cycle in sample_cycles:
            print(f"     Cycle: {cycle.get('cycleName', 'N/A')}")
            print(f"     Status: {cycle.get('status', 'N/A')}")
            print(f"     Year: {cycle.get('cycleYear', 'N/A')}")
            print(f"     Month: {cycle.get('cycleMonth', 'N/A')}")
            print()
    
    # Check customers
    print(f"\n1d. CHECKING CUSTOMERS...")
    customers = db.customers
    customers_count = customers.count_documents({})
    print(f"   Total customers: {customers_count}")
    
    # Check products
    print(f"\n1e. CHECKING PRODUCTS...")
    products = db.products
    products_count = products.count_documents({})
    print(f"   Total products: {products_count}")
    
except Exception as e:
    print(f"   [ERROR] MongoDB connection failed: {e}")
    exit(1)

# Step 2: Login as admin
print(f"\n2. LOGGING IN AS ADMIN...")
try:
    admin_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@heavygarlic.com", "password": "admin123"},
        headers={"Content-Type": "application/json"}
    )
    
    if admin_response.status_code != 200:
        print(f"   [ERROR] Admin login failed: {admin_response.status_code}")
        print(f"   Response: {admin_response.text}")
        exit(1)
    
    admin_data = admin_response.json()
    admin_token = admin_data.get("access_token")
    print(f"   [OK] Admin logged in successfully")
    
except Exception as e:
    print(f"   [ERROR] Admin login failed: {e}")
    exit(1)

# Step 3: Test report generation for November 2024
print(f"\n3. TESTING REPORT GENERATION FOR NOVEMBER 2024...")

# Test different report types
report_tests = [
    {
        "name": "Sales Summary Report",
        "params": {
            "reportType": "sales_summary",
            "format": "excel",
            "startDate": "2024-11-01",
            "endDate": "2024-11-30",
            "includeCharts": True,
            "includeRawData": True
        }
    },
    {
        "name": "Sales Summary Report (All Data)",
        "params": {
            "reportType": "sales_summary",
            "format": "excel",
            "includeCharts": True,
            "includeRawData": True
        }
    }
]

for test in report_tests:
    print(f"\n3a. Testing {test['name']}...")
    try:
        response = requests.post(
            f"{BASE_URL}/reports/generate",
            json=test['params'],
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            timeout=60
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"   [SUCCESS] Report generated successfully")
            
            # Try to get the report content
            if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in response.headers.get('content-type', ''):
                print(f"   [OK] Received Excel file")
                # Save the file for inspection
                filename = f"test_report_{test['name'].replace(' ', '_').lower()}.xlsx"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"   [OK] Saved report as: {filename}")
                
                # Try to read the Excel file
                try:
                    df = pd.read_excel(filename)
                    print(f"   Excel file contents:")
                    print(f"     Rows: {len(df)}")
                    print(f"     Columns: {list(df.columns)}")
                    if len(df) > 0:
                        print(f"     First few rows:")
                        print(df.head().to_string())
                    else:
                        print(f"     [WARNING] Excel file is empty!")
                except Exception as e:
                    print(f"   [ERROR] Could not read Excel file: {e}")
                    
        elif response.status_code == 202:
            print(f"   [INFO] Report generation started (async)")
            report_data = response.json()
            print(f"   Report ID: {report_data.get('reportId')}")
            print(f"   Status: {report_data.get('status')}")
            
        else:
            print(f"   [ERROR] Report generation failed")
            print(f"   Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"   [ERROR] Report test failed: {e}")

# Step 4: Test direct API endpoints
print(f"\n4. TESTING DIRECT API ENDPOINTS...")

# Test sales history endpoint
print(f"\n4a. Testing sales history endpoint...")
try:
    sales_response = requests.get(
        f"{BASE_URL}/sales-history?start_date=2024-11-01&end_date=2024-11-30",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    print(f"   Sales history status: {sales_response.status_code}")
    if sales_response.status_code == 200:
        sales_data = sales_response.json()
        print(f"   Sales history response:")
        print(f"     Total records: {sales_data.get('total', 0)}")
        print(f"     Data length: {len(sales_data.get('data', []))}")
        
        if sales_data.get('data'):
            print(f"     Sample record:")
            sample = sales_data['data'][0]
            print(f"       Customer: {sample.get('customerName', 'N/A')}")
            print(f"       Product: {sample.get('productDescription', 'N/A')}")
            print(f"       Quantity: {sample.get('quantity', 0)}")
            print(f"       Total Sales: ${sample.get('totalSales', 0):.2f}")
    else:
        print(f"   [ERROR] Sales history request failed: {sales_response.text[:200]}")
        
except Exception as e:
    print(f"   [ERROR] Sales history test failed: {e}")

# Step 5: Check report generation logic
print(f"\n5. ANALYZING REPORT GENERATION ISSUE...")

# Check if there's a mismatch between database data and API response
print(f"\n5a. Comparing database vs API data...")

# Get data directly from database
try:
    db_sales_data = list(sales_history.find({"year": 2024, "month": 11}).limit(10))
    print(f"   Database November 2024 records: {len(db_sales_data)}")
    
    if db_sales_data:
        total_db_sales = sum(record.get('totalSales', 0) for record in db_sales_data)
        print(f"   Database total sales (sample): ${total_db_sales:.2f}")
        
        # Check if the data structure matches what the API expects
        sample_record = db_sales_data[0]
        print(f"   Sample record structure:")
        for key, value in sample_record.items():
            print(f"     {key}: {type(value).__name__} = {value}")
    
except Exception as e:
    print(f"   [ERROR] Database analysis failed: {e}")

print(f"\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)

print(f"\nSUMMARY:")
print(f"1. Check if November 2024 data exists in MongoDB")
print(f"2. Verify the data structure matches API expectations")
print(f"3. Test report generation with different parameters")
print(f"4. Check if there are date format issues")
print(f"5. Verify the report generation logic is working correctly")
