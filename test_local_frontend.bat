@echo off
echo ========================================
echo Testing Local Frontend
echo ========================================
echo.

echo Starting local frontend server...
cd sop-portal-frontend

echo Installing dependencies...
npm install

echo Starting Vite development server...
npm run dev

pause

