@echo off
REM ========================================
REM   S&OP Portal - Stop All Services
REM ========================================

title Stop S&OP Portal

echo.
echo ========================================
echo    Stopping S&OP Portal Services
echo ========================================
echo.

color 0C

REM ========================================
REM   Stop Frontend (Node.js/Vite)
REM ========================================
echo [1/3] Stopping Frontend Dev Server...

REM Kill Node.js processes on port 5173
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo Stopping process ID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

REM Also kill any node processes running npm dev
tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I /N "node.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Stopping Node.js processes...
    taskkill /F /IM node.exe /T >nul 2>&1
)

echo [OK] Frontend stopped
echo.

REM ========================================
REM   Stop Backend (Python/FastAPI)
REM ========================================
echo [2/3] Stopping Backend API...

REM Kill Python processes on port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Stopping process ID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

REM Also kill Python processes running uvicorn
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Stopping Python processes...
    taskkill /F /IM python.exe /T >nul 2>&1
)

echo [OK] Backend stopped
echo.

REM ========================================
REM   Stop MongoDB
REM ========================================
echo [3/3] Stopping MongoDB...

tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Stopping MongoDB gracefully...
    taskkill /F /IM mongod.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo [OK] MongoDB stopped
) else (
    echo [INFO] MongoDB was not running
)
echo.

REM ========================================
REM   Cleanup Complete
REM ========================================
echo.
echo ========================================
echo    All Services Stopped Successfully!
echo ========================================
echo.
echo All S&OP Portal services have been stopped.
echo You can now close this window.
echo.
pause
