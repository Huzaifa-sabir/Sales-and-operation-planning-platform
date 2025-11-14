@echo off
echo ========================================
echo Testing CORS Issue - Frontend vs Backend
echo ========================================
echo.

echo 1. Checking Backend CORS Configuration...
echo Backend URL: https://sales-and-operation-planning-platform-1.onrender.com
echo Frontend URL: https://soptest.netlify.app
echo.

echo 2. Testing OPTIONS request (CORS Preflight)...
curl -X OPTIONS "https://sales-and-operation-planning-platform-1.onrender.com/api/v1/products" ^
  -H "Origin: https://soptest.netlify.app" ^
  -H "Access-Control-Request-Method: GET" ^
  -H "Access-Control-Request-Headers: Content-Type,Authorization" ^
  -v
echo.
echo.

echo 3. Testing GET request with Origin header...
curl -X GET "https://sales-and-operation-planning-platform-1.onrender.com/api/v1/products?page=1&limit=5" ^
  -H "Origin: https://soptest.netlify.app" ^
  -H "Accept: application/json" ^
  -v
echo.
echo.

echo 4. Testing without Origin header (should work)...
curl -X GET "https://sales-and-operation-planning-platform-1.onrender.com/api/v1/products?page=1&limit=5" ^
  -H "Accept: application/json"
echo.
echo.

echo ========================================
echo CORS Test Results:
echo - If you see "Access-Control-Allow-Origin" headers, CORS is working
echo - If you see "No 'Access-Control-Allow-Origin' header", CORS is broken
echo ========================================
pause

