@echo off
echo ========================================
echo 🛑 Stopping S&OP Portal Development
echo ========================================
echo.

echo Stopping Backend Server...
taskkill /f /im python.exe > nul 2>&1
echo ✅ Backend stopped

echo Stopping Frontend Server...
taskkill /f /im node.exe > nul 2>&1
echo ✅ Frontend stopped

echo Stopping any remaining processes...
taskkill /f /im cmd.exe /fi "WINDOWTITLE eq Backend*" > nul 2>&1
taskkill /f /im cmd.exe /fi "WINDOWTITLE eq Frontend*" > nul 2>&1

echo.
echo ✅ All development servers stopped
echo.
pause

