@echo off
echo ================================================================================
echo Starting AI Commit Generator Web Interface
echo ================================================================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Starting Flask API server...
start cmd /k "python api_server.py"

timeout /t 3

echo.
echo Installing Node.js dependencies...
cd frontend
call npm install

echo.
echo Starting React development server...
call npm start

pause
