@echo off
REM ========================================
REM   S&OP Portal - Status Check
REM ========================================

title S&OP Portal Status

:check
cls
echo.
echo ========================================
echo      S&OP Portal - Service Status
echo ========================================
echo      Updated: %date% %time%
echo ========================================
echo.

color 0B

REM Check MongoDB
echo [1] MongoDB Database
echo     Port: 27017
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo     Status: [RUNNING] ✓
    color 0A
) else (
    echo     Status: [STOPPED] ✗
    color 0C
)
echo.

REM Check Backend
echo [2] Backend API (FastAPI)
echo     Port: 8000
netstat -ano | findstr ":8000" | findstr "LISTENING" >NUL
if "%ERRORLEVEL%"=="0" (
    echo     Status: [RUNNING] ✓
    echo     URL: http://localhost:8000
    echo     Docs: http://localhost:8000/api/docs
    color 0A
) else (
    echo     Status: [STOPPED] ✗
    color 0C
)
echo.

REM Check Frontend
echo [3] Frontend (Vite Dev Server)
echo     Port: 5173
netstat -ano | findstr ":5173" | findstr "LISTENING" >NUL
if "%ERRORLEVEL%"=="0" (
    echo     Status: [RUNNING] ✓
    echo     URL: http://localhost:5173
    color 0A
) else (
    echo     Status: [STOPPED] ✗
    color 0C
)
echo.

echo ========================================
echo.
echo [R] Refresh Status
echo [O] Open Frontend in Browser
echo [D] Open API Docs in Browser
echo [S] Start All Services
echo [X] Stop All Services
echo [Q] Quit
echo.
echo ========================================
echo.

choice /C RODSXQ /N /M "Select an option: "

if errorlevel 6 goto :end
if errorlevel 5 goto :stop
if errorlevel 4 goto :start
if errorlevel 3 goto :opendocs
if errorlevel 2 goto :openbrowser
if errorlevel 1 goto :check

:openbrowser
start http://localhost:5173
goto :check

:opendocs
start http://localhost:8000/api/docs
goto :check

:start
start "" "d:\Heavy\start-sop-portal.bat"
timeout /t 3 /nobreak >nul
goto :check

:stop
start "" "d:\Heavy\stop-sop-portal.bat"
timeout /t 3 /nobreak >nul
goto :check

:end
exit
