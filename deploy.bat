@echo off
REM Build and Deploy ServeQ

echo Building frontend...
cd frontend
call npm install
call npm run build

echo.
echo  Frontend built successfully
echo  Build output ready in backend\static
echo.
echo  Ready for deployment!
echo.
echo Next steps:
echo 1. Push to GitHub
echo 2. Connect to Render.com or Railway.app
echo 3. Set VITE_API_URL environment variable
echo 4. Deploy!
