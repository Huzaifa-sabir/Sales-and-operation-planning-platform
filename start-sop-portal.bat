@echo off
REM ========================================
REM   S&OP Portal - Complete Startup Script
REM ========================================
REM   This script starts:
REM   1. MongoDB Database
REM   2. Backend API (FastAPI)
REM   3. Frontend Dev Server (React + Vite)
REM ========================================

title S&OP Portal Startup

echo.
echo ========================================
echo    Starting S&OP Portal Application
echo ========================================
echo.

REM Set colors
color 0A

REM Check if running as administrator (MongoDB might need it)
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [WARNING] Not running as Administrator
    echo MongoDB might fail to start if data directory needs permissions
    echo.
    timeout /t 3 >nul
)

REM ========================================
REM   1. Start MongoDB
REM ========================================
echo [1/3] Starting MongoDB...
echo.

REM Check if MongoDB is already running
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] MongoDB is already running
    echo.
) else (
    REM Create data directory if it doesn't exist
    if not exist "d:\Heavy\mongodb-data" (
        echo Creating MongoDB data directory...
        mkdir "d:\Heavy\mongodb-data"
    )

    REM Start MongoDB in a new window
    echo Starting MongoDB server...
    start "MongoDB Server" /MIN "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --dbpath "d:\Heavy\mongodb-data" --port 27017

    REM Wait for MongoDB to start
    echo Waiting for MongoDB to start...
    timeout /t 5 /nobreak >nul

    REM Verify MongoDB started
    tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
    if "%ERRORLEVEL%"=="0" (
        echo [OK] MongoDB started successfully
        echo MongoDB running on: mongodb://localhost:27017
    ) else (
        echo [ERROR] Failed to start MongoDB
        echo Please check if MongoDB is installed at: C:\Program Files\MongoDB\Server\8.0\bin\
        echo.
        pause
        exit /b 1
    )
)
echo.

REM ========================================
REM   2. Start Backend API (FastAPI)
REM ========================================
echo [2/3] Starting Backend API...
echo.

REM Check if Python virtual environment exists
if not exist "d:\Heavy\sop-portal-backend\venv" (
    echo [ERROR] Python virtual environment not found!
    echo Please create it first by running:
    echo   cd sop-portal-backend
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Start Backend in a new window
cd /d "d:\Heavy\sop-portal-backend"
start "Backend API - FastAPI" cmd /k "venv\Scripts\activate && python run.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul
echo [OK] Backend API starting...
echo Backend running on: http://localhost:8000
echo API Docs available at: http://localhost:8000/api/docs
echo.

REM ========================================
REM   3. Start Frontend Dev Server (Vite)
REM ========================================
echo [3/3] Starting Frontend Dev Server...
echo.

REM Check if node_modules exists
if not exist "d:\Heavy\sop-portal-frontend\node_modules" (
    echo [WARNING] node_modules not found!
    echo Installing dependencies...
    cd /d "d:\Heavy\sop-portal-frontend"
    call npm install
    echo.
)

REM Start Frontend in a new window
cd /d "d:\Heavy\sop-portal-frontend"
start "Frontend - Vite Dev Server" cmd /k "npm run dev"

echo Waiting for frontend to start...
timeout /t 8 /nobreak >nul
echo [OK] Frontend starting...
echo.

REM ========================================
REM   Startup Complete!
REM ========================================
echo.
echo ========================================
echo    All Services Started Successfully!
echo ========================================
echo.
echo  MongoDB:  mongodb://localhost:27017
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/api/docs
echo  Frontend: http://localhost:5173
echo.
echo ========================================
echo.
echo Opening frontend in browser...
timeout /t 3 /nobreak >nul

REM Open frontend in default browser
start http://localhost:5173

echo.
echo [INFO] Default credentials:
echo   Email:    admin@heavygarlic.com
echo   Password: admin123
echo.
echo [IMPORTANT] Change these credentials after first login!
echo.
echo ========================================
echo.
echo Press any key to view service status...
pause >nul

REM Show service status
cls
echo.
echo ========================================
echo      Service Status Check
echo ========================================
echo.

echo [MongoDB Status]
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo  Status: RUNNING
) else (
    echo  Status: NOT RUNNING
)
echo.

echo [Backend Status]
netstat -ano | findstr ":8000" >NUL
if "%ERRORLEVEL%"=="0" (
    echo  Status: RUNNING on port 8000
) else (
    echo  Status: NOT RUNNING
)
echo.

echo [Frontend Status]
netstat -ano | findstr ":5173" >NUL
if "%ERRORLEVEL%"=="0" (
    echo  Status: RUNNING on port 5173
) else (
    echo  Status: NOT RUNNING
)
echo.

echo ========================================
echo.
echo To stop all services, run: stop-sop-portal.bat
echo.
echo This window can be closed safely.
echo The services will continue running in their own windows.
echo.
pause
