@echo off
echo Starting conversion...
echo ------------------------------------------

:: Check if python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not added to your PATH.
    pause
    exit /b
)

:: Run the python script
python json_to_md.py

echo ------------------------------------------
echo Done.
pause