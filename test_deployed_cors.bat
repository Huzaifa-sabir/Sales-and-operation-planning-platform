@echo off
echo ========================================
echo Testing Deployed Backend CORS
echo ========================================
echo.

echo 1. Testing deployed backend CORS headers...
curl -X OPTIONS "https://sales-and-operation-planning-platform-1.onrender.com/api/v1/products" ^
  -H "Origin: https://soptest.netlify.app" ^
  -H "Access-Control-Request-Method: GET" ^
  -H "Access-Control-Request-Headers: Content-Type,Authorization" ^
  -v
echo.
echo.

echo 2. Testing GET request with Origin header...
curl -X GET "https://sales-and-operation-planning-platform-1.onrender.com/api/v1/products?page=1&limit=5" ^
  -H "Origin: https://soptest.netlify.app" ^
  -H "Accept: application/json" ^
  -v
echo.
echo.

echo ========================================
echo CORS Test Results:
echo - Look for "Access-Control-Allow-Origin: https://soptest.netlify.app"
echo - If missing, the deployed backend needs to be updated
echo ========================================
pause

