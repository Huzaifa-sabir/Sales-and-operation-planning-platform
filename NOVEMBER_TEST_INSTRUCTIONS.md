# November 2025 Sales Report Test Instructions

## What Was Done

### 1. Added November 2025 Test Data
- **Script**: `add_november_sales_data.py`
- **Records Added**: 25 sales transactions
- **Data Summary**:
  - Total Revenue: $161,750.00
  - Total Quantity: 2,750 units
  - Transactions: 25
  - Customers: 5 (from existing customers in database)
  - Products: 5 (from existing products in database)
  - Date: November 2025 (year=2025, month=11)

### 2. Database Updated
- Collection: `salesHistory`
- New records with: `year: 2025, monthNum: 11`
- Each record includes:
  - Customer ID and Name
  - Product ID and Description
  - Quantity, Unit Price, Total Sales
  - Cost Price, Gross Profit
  - Sales Rep information

## How to Test the Report

### Option 1: Test Locally (if backend running)

1. **Make sure MongoDB has the November data**:
```bash
python add_november_sales_data.py
```

2. **Start backend**:
```bash
cd sop-portal-backend
uvicorn app.main:app --reload
```

3. **Run test script**:
```bash
python test_november_report_with_curl.py
```

4. **Check the generated Excel file**:
- File will be named: `november_2025_sales_report_YYYYMMDD_HHMMSS.xlsx`
- Open it and verify data

### Option 2: Test on Render (Deployed Backend)

**IMPORTANT**: You need to add the November data to your Render database first!

1. **Connect to Render MongoDB and add data**:
```bash
# Set your Render MongoDB URI
export MONGODB_URI="your-render-mongodb-uri"

# Run the script to add November data
python add_november_sales_data.py
```

2. **Update test script with your Render URL**:
Edit `test_november_report_with_curl.py`:
```python
BACKEND_URL = "https://your-backend-app.onrender.com/api/v1"
```

3. **Run the test**:
```bash
python test_november_report_with_curl.py
```

### Option 3: Test from Frontend UI

1. **Push the data mapping fix to Render** (already done)
   - Commit: `1913643` - Fix report data mapping

2. **Wait for Render deployment** (2-5 minutes)

3. **Add November data to Render database**:
   - Either: Connect to Render MongoDB and run `add_november_sales_data.py`
   - Or: If you're using the same local MongoDB, data is already there!

4. **Login to deployed frontend**:
   - Go to your frontend URL on Render/Vercel

5. **Navigate to Reports page**

6. **Select "Sales Summary Report"**

7. **Set filters**:
   - Year: 2025
   - Month: November (11)

8. **Click "Generate Excel"**

9. **Verify downloaded file**:
   - Should show: Total Revenue ~$161,750
   - Should show: Total Quantity ~2,750
   - Should show: 25 transactions
   - Should list 5 customers
   - Should list 5 products

## Expected Excel Report Content

### Sheet 1: Sales Summary

**Header Section:**
- Generated At: [timestamp]
- Report Type: Sales Summary

**Overall Statistics:**
- Total Revenue: $161,750.00
- Total Quantity: 2,750.00
- Transactions: 25
- Avg Quantity/Transaction: 110.00
- Avg Unit Price: $58.82

**Monthly Trends:**
- 2025-11: Revenue: $161,750.00, Quantity: 2,750.00, Transactions: 25

**Top Customers:**
(All 5 customers should appear with their revenue)
1. Industria Los Patitos, S.A.
2. Canadawide Fruit Wholesalers Inc.
3. [Other customers]

**Top Products:**
(All 5 products should appear with quantities)
1. Peeled Garlic 12x1 LB Garland
2. Peeled Garlic 12x3 LB Garland
3. Garlic Puree 40 LB Bag
4. [Other products]

## Troubleshooting

### Issue: Report shows $0.00
**Solution**: Data mapping fix needs to be deployed
- Check commit `1913643` is deployed on Render
- Verify collection name changed from `sales_history` to `salesHistory`
- Verify field name changed from `quantitySold` to `quantity`

### Issue: No November data appears
**Cause**: November data not in the deployed database
**Solution**:
1. Connect to your Render MongoDB
2. Run: `python add_november_sales_data.py` with Render MongoDB URI
3. Verify: Check that `db.salesHistory.count_documents({"year": 2025, "monthNum": 11})` returns 25

### Issue: Report takes too long
**Cause**: Using old polling endpoint instead of instant download
**Solution**:
- Check that frontend uses `/reports/generate-instant` endpoint
- Commit `6a22850` should be deployed with instant download feature

### Issue: Download doesn't start
**Cause**: Frontend not updated or blob handling issue
**Solution**:
- Check browser console for errors
- Verify frontend deployment includes changes to `Reports.tsx` and `reports.ts`
- Try different browser

## Files Created

1. `add_november_sales_data.py` - Script to add test data
2. `test_november_report_with_curl.py` - Automated test script
3. `NOVEMBER_TEST_INSTRUCTIONS.md` - This file

## Summary

✅ **What's Ready**:
- November 2025 test data (25 records, $161,750 revenue)
- Data mapping fixes (correct collection and field names)
- Instant download feature (no polling)
- Test scripts for verification

⚠️ **What You Need To Do**:
1. Ensure November data is in your deployed MongoDB (run `add_november_sales_data.py`)
2. Wait for Render to deploy the latest changes
3. Test report generation from UI or run test script
4. Verify Excel file shows correct November 2025 data

📊 **Expected Result**:
Click "Generate Excel" → 3-10 seconds → Download starts → Excel file shows $161,750 revenue from November 2025 data!
