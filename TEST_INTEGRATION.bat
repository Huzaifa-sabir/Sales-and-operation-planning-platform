@echo off
echo ========================================
echo    S&OP Portal - Integration Test
echo ========================================
echo.

echo [1/4] Testing Backend Health...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -Method GET; Write-Host '✅ Backend Status:' $response.StatusCode; Write-Host 'Response:' $response.Content } catch { Write-Host '❌ Backend Error:' $_.Exception.Message; exit 1 }"

echo.
echo [2/4] Testing CORS...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/auth/login' -Method OPTIONS -Headers @{'Origin'='http://localhost:5173'}; Write-Host '✅ CORS Status:' $response.StatusCode } catch { Write-Host '❌ CORS Error:' $_.Exception.Message }"

echo.
echo [3/4] Testing Login Endpoint...
powershell -Command "$body = '{\"username\":\"admin@heavygarlic.com\",\"password\":\"admin123\"}'; try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/auth/login' -Method POST -Body $body -ContentType 'application/json'; Write-Host '✅ Login Status:' $response.StatusCode; Write-Host 'Response:' $response.Content } catch { Write-Host '❌ Login Error:' $_.Exception.Message }"

echo.
echo [4/4] Testing Frontend Connection...
echo Opening frontend in browser...
start http://localhost:5173

echo.
echo ========================================
echo    Test Complete!
echo ========================================
echo.
echo If all tests passed, try logging in with:
echo Email: admin@heavygarlic.com
echo Password: admin123
echo.
pause
