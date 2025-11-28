@echo off
echo ================================================================================
echo Starting AI Commit Generator (Fresh Start)
echo ================================================================================
echo.

echo Cleaning up old cloned repositories...
if exist cloned_repos (
    echo Removing readonly attributes...
    attrib -r -h cloned_repos\*.* /s /d
    rmdir /s /q cloned_repos
    echo Done!
) else (
    echo No old repositories to clean.
)

echo.
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo ================================================================================
echo Starting Flask API server...
echo ================================================================================
start cmd /k "python api_server.py"

timeout /t 3

echo.
echo ================================================================================
echo Starting React development server...
echo ================================================================================
cd frontend
start cmd /k "npm start"

echo.
echo ================================================================================
echo System is starting!
echo ================================================================================
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo The browser will open automatically in a few seconds...
echo.
pause
