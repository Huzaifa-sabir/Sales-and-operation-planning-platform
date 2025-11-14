@echo off
echo ========================================
echo 🛠️ S&OP Portal Development Setup
echo ========================================
echo.

echo 📦 Setting up development environment...
echo.

echo 1. Installing Backend Dependencies...
cd sop-portal-backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Backend dependencies failed to install
    pause
    exit /b 1
)
echo ✅ Backend dependencies installed
echo.

echo 2. Installing Frontend Dependencies...
cd ../sop-portal-frontend
npm install
if %errorlevel% neq 0 (
    echo ❌ Frontend dependencies failed to install
    pause
    exit /b 1
)
echo ✅ Frontend dependencies installed
echo.

echo 3. Setting up environment variables...
echo VITE_API_URL=http://localhost:8000/api/v1 > .env.local
echo ✅ Frontend configured for local backend
echo.

echo 4. Testing database connection...
cd ../sop-portal-backend
python -c "import asyncio; from app.config.database import db; asyncio.run(db.connect_db()); print('✅ Database connection successful')"
if %errorlevel% neq 0 (
    echo ❌ Database connection failed
    pause
    exit /b 1
)
echo ✅ Database connection successful
echo.

echo ========================================
echo 🎉 Setup Complete!
echo ========================================
echo.
echo Run 'start_all.bat' to start development servers
echo.
pause

