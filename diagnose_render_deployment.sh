#!/bin/bash

echo "================================================================================"
echo "RENDER DEPLOYMENT DIAGNOSIS - Report Generation Issue"
echo "================================================================================"

BACKEND_URL="https://sales-and-operation-planning-platform-1.onrender.com"

echo ""
echo "[1] Testing Backend Health..."
curl -s "$BACKEND_URL/" | jq '.'

echo ""
echo "[2] Checking Latest Commit Deployed..."
echo "Expected: commit 7f05164 (CRITICAL FIX: Use monthNum instead of month)"
curl -s "$BACKEND_URL/api/docs" | grep -o "version.*" | head -1

echo ""
echo "[3] Testing Report Endpoint EXISTS..."
curl -s -o /dev/null -w "Status: %{http_code}\n" "$BACKEND_URL/api/v1/reports/generate-instant"

echo ""
echo "[4] Checking if monthNum fix is deployed..."
echo "This requires testing actual report generation with authentication"
echo "Manual test needed: Login and generate report from https://soptest.netlify.app/reports"

echo ""
echo "================================================================================"
echo "NEXT STEPS:"
echo "================================================================================"
echo "1. Check Render dashboard - is deployment 'Live'?"
echo "2. Check environment variables - is MONGODB_URI correct?"
echo "3. Check Render logs for any errors during report generation"
echo "4. Manually test: soptest.netlify.app/reports -> Generate Report"
echo ""
echo "If still showing \$0.00:"
echo "- Deployment may not be complete"
echo "- MongoDB Atlas may not have the November data"
echo "- Backend may be connecting to wrong MongoDB database"
echo "================================================================================"
