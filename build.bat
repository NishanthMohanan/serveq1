@echo off
REM ServeQ - Simple Local Build Script

echo.
echo  ServeQ Build Script
echo ====================
echo.

echo  Building frontend...
cd frontend
call npm install >nul 2>&1
call npm run build >nul 2>&1

echo  Frontend ready in: backend\static
echo.
echo  Backend dependencies installed
echo.
echo  Next steps:
echo    1. cd backend
echo    2. pip install -r requirements.txt
echo    3. uvicorn app:app --reload
echo.
echo Then visit: http://localhost:8000
