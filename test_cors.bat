@echo off
echo ========================================
echo Testing S&OP Portal CORS Configuration
echo ========================================
echo.

echo 1. Testing Backend Health Check...
curl -X GET "https://sales-and-operation-planning-platform-1.onrender.com/health" -H "Accept: application/json"
echo.
echo.

echo 2. Testing CORS Preflight Request...
curl -X OPTIONS "https://sales-and-operation-planning-platform-1.onrender.com/api/v1/products" -H "Origin: https://soptest.netlify.app" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: Content-Type,Authorization" -v
echo.
echo.

echo 3. Testing Products API with CORS...
curl -X GET "https://sales-and-operation-planning-platform-1.onrender.com/api/v1/products?page=1&limit=5" -H "Origin: https://soptest.netlify.app" -H "Accept: application/json" -v
echo.
echo.

echo 4. Testing Login API...
curl -X POST "https://sales-and-operation-planning-platform-1.onrender.com/api/v1/auth/login" -H "Content-Type: application/json" -H "Origin: https://soptest.netlify.app" -d "{\"email\":\"admin@heavygarlic.com\",\"password\":\"admin123\"}" -v
echo.
echo.

echo ========================================
echo CORS Test Complete
echo ========================================
pause

