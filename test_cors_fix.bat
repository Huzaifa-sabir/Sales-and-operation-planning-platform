@echo off
echo ========================================
echo Testing CORS Fix - Local vs Deployed
echo ========================================
echo.

echo 1. Testing LOCAL backend CORS configuration...
cd sop-portal-backend
python -c "from app.config.settings import settings; print('Local CORS_ORIGINS:', settings.CORS_ORIGINS); print('Netlify in list:', 'https://soptest.netlify.app' in settings.cors_origins_list)"
echo.

echo 2. Starting LOCAL backend server...
echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python run.py
