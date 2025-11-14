@echo off
echo ========================================
echo Testing Frontend with Local Backend
echo ========================================
echo.

echo 1. Starting LOCAL frontend server...
cd sop-portal-frontend

echo 2. Updating API URL to local backend...
echo VITE_API_URL=http://localhost:8000/api/v1 > .env.local

echo 3. Installing dependencies...
npm install

echo 4. Starting Vite development server...
echo Frontend will be available at http://localhost:5173
echo Backend should be running at http://localhost:8000
echo.
npm run dev

