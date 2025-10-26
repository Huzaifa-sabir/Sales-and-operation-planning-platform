@echo off
echo ========================================
echo Starting S&OP Portal Local Development
echo ========================================
echo.

echo 🚀 Starting Backend Server...
echo Backend will run on: http://localhost:8000
echo API Docs: http://localhost:8000/api/docs
echo.

cd sop-portal-backend
start "Backend Server" cmd /k "python run.py"

echo.
echo ⏳ Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo 🌐 Starting Frontend Server...
echo Frontend will run on: http://localhost:5173
echo.

cd ../sop-portal-frontend
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ========================================
echo 🎉 Development Environment Started!
echo ========================================
echo.
echo 📊 Backend: http://localhost:8000
echo 🌐 Frontend: http://localhost:5173
echo 📚 API Docs: http://localhost:8000/api/docs
echo 🗄️ Database: MongoDB Atlas (Cloud)
echo.
echo 🔑 Login Credentials:
echo    Email: admin@heavygarlic.com
echo    Password: admin123
echo.
echo Press any key to stop all servers...
pause > nul

echo.
echo 🛑 Stopping servers...
taskkill /f /im python.exe > nul 2>&1
taskkill /f /im node.exe > nul 2>&1
echo ✅ All servers stopped.
