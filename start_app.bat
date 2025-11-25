@echo off
echo ================================================================================
echo Starting AI Commit Message Generator
echo ================================================================================
echo.

echo Starting Flask API Server...
start cmd /k "python api_server.py"

timeout /t 3 /nobreak > nul

echo Starting React Frontend...
cd frontend
start cmd /k "npm start"

echo.
echo ================================================================================
echo Application started!
echo API: http://localhost:5000
echo Frontend: http://localhost:3000
echo ================================================================================
