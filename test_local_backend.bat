@echo off
echo ========================================
echo Testing Local Backend CORS
echo ========================================
echo.

echo Starting local backend server...
cd sop-portal-backend

echo Installing dependencies...
pip install -r requirements.txt

echo Starting FastAPI server...
python run.py

pause
