@echo off
:: Sets the title of the command prompt window
title Markdown Chapter Generator

echo.
echo ==========================================
echo   Status: Ready to generate 10 files
echo ==========================================
echo.

:: This runs your python script
:: Make sure 'create_raw_afterglows.py' is in the same folder!
python create_raw_afterglows.py

echo.
echo ==========================================
echo               Job Complete
echo ==========================================
echo.

:: This command prevents the window from closing immediately
:: so you can read the file names above.
pause