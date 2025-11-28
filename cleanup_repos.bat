@echo off
echo ================================================================================
echo Cleaning Up Cloned Repositories
echo ================================================================================
echo.

if not exist cloned_repos (
    echo No cloned repositories found.
    echo Nothing to clean up.
    pause
    exit /b 0
)

echo Found cloned_repos folder. Cleaning up...
echo.

echo Step 1: Removing readonly attributes...
attrib -r -h cloned_repos\*.* /s /d 2>nul

echo Step 2: Removing files...
rmdir /s /q cloned_repos 2>nul

if exist cloned_repos (
    echo.
    echo Warning: Some files could not be deleted.
    echo This might be because:
    echo   - Files are in use by another program
    echo   - Git processes are still running
    echo.
    echo Please:
    echo   1. Close any programs using these files
    echo   2. Stop the Flask server if running
    echo   3. Run this script again
    echo.
) else (
    echo.
    echo ================================================================================
    echo ✅ Cleanup completed successfully!
    echo ================================================================================
    echo.
)

pause
