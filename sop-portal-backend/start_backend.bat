@echo off
echo ========================================
echo    S&OP Portal Backend - Starting
echo ========================================
echo.
echo Starting backend server...
echo.
cd /d "%~dp0"
python working_backend.py
pause