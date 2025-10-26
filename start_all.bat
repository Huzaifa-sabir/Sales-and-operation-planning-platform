@echo off
title S&OP Portal - Local Development

echo ========================================
echo 🚀 S&OP Portal Local Development
echo ========================================
echo.

echo 📦 Installing dependencies...
echo.

echo Installing Backend Dependencies...
cd sop-portal-backend
pip install -r requirements.txt
echo ✅ Backend dependencies installed
echo.

echo Installing Frontend Dependencies...
cd ../sop-portal-frontend
npm install
echo ✅ Frontend dependencies installed
echo.

echo 🚀 Starting Backend Server...
cd ../sop-portal-backend
start "Backend" cmd /k "echo Backend Server Starting... && python run.py"

echo ⏳ Waiting 3 seconds...
timeout /t 3 /nobreak > nul

echo 🌐 Starting Frontend Server...
cd ../sop-portal-frontend
start "Frontend" cmd /k "echo Frontend Server Starting... && npm run dev"

echo.
echo ========================================
echo 🎉 Development Environment Ready!
echo ========================================
echo.
echo 📊 Backend: http://localhost:8000
echo 🌐 Frontend: http://localhost:5173
echo 📚 API Docs: http://localhost:8000/api/docs
echo.
echo 🔑 Login: admin@heavygarlic.com / admin123
echo.
echo Press Ctrl+C to stop all servers
echo ========================================

:loop
timeout /t 1 /nobreak > nul
goto loop
