@echo off
echo ================================================================================
echo AI Commit Generator - Starting Application
echo ================================================================================
echo.

echo Installing Python dependencies...
cd backend
pip install -r requirements.txt
cd ..

echo.
echo Starting Flask API server...
start cmd /k "cd backend && python api_server.py"

timeout /t 3

echo.
echo Starting React development server...
cd frontend
start cmd /k "npm start"

echo.
echo ================================================================================
echo Application is starting!
echo ================================================================================
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
pause
