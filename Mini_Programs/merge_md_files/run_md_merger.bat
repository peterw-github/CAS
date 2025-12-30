@echo off
TITLE Markdown Auto-Merger
echo Searching for files to merge...
echo.

:: Runs the python script
python md_merger.py

echo.
echo ========================================================
echo Job done. Check the folder for 'output.md'.
echo ========================================================
pause