@echo off
title Cortana Identity File Renamer
echo ========================================================
echo      STARTING CORTANA IDENTITY FILE RENAMER
echo ========================================================
echo.

:: Check if python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not added to PATH.
    pause
    exit /b
)

:: Run the python script
python "title_extractor.py"

echo.
echo ========================================================
echo                 OPERATION FINISHED
echo ========================================================
pause