@echo off
echo ========================================
echo Testing CORS Fix on Render Deployment
echo ========================================
echo.

echo 🔍 Testing CORS configuration...
echo.

echo 1. Testing debug endpoint...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://sales-and-operation-planning-platform-1.onrender.com/debug/cors' -Method GET; Write-Host '✅ Debug endpoint accessible'; Write-Host $response.Content } catch { Write-Host '❌ Debug endpoint failed:' $_.Exception.Message }"
echo.

echo 2. Testing CORS preflight request...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://sales-and-operation-planning-platform-1.onrender.com/api/v1/customers' -Method OPTIONS -Headers @{'Origin'='https://soptest.netlify.app'; 'Access-Control-Request-Method'='GET'}; Write-Host '✅ CORS preflight successful'; Write-Host 'Headers:'; $response.Headers | Format-Table } catch { Write-Host '❌ CORS preflight failed:' $_.Exception.Message }"
echo.

echo 3. Testing actual API request...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://sales-and-operation-planning-platform-1.onrender.com/api/v1/customers' -Method GET -Headers @{'Origin'='https://soptest.netlify.app'}; Write-Host '✅ API request successful'; Write-Host 'Status:' $response.StatusCode } catch { Write-Host '❌ API request failed:' $_.Exception.Message }"
echo.

echo ========================================
echo Test Complete!
echo ========================================
echo.
echo If all tests show ✅, CORS is fixed!
echo If any show ❌, wait 5-10 minutes for deployment
echo.
pause

