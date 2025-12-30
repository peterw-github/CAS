@echo off
TITLE Markdown Auto-Renamer

echo ==================================================
echo      STARTING MARKDOWN BULK RENAME PROCESS
echo ==================================================
echo.

:: Check if Python is reachable
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python to use this tool.
    pause
    exit /b
)

:: Run the Python script
python bulk_rename.py

echo.
echo ==================================================
echo                 PROCESS COMPLETE
echo ==================================================
echo.
echo Press any key to close this window...
pause >nul