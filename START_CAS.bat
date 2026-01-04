@echo off

:: 1. HARDCODE THE PATH TO YOUR CODE FOLDER
cd /d "D:\CAS" 

:: 2. Point to your Python (same as before)
set PYTHON_EXE="D:/CAS/.venv/Scripts/python.exe"

echo Starting CAS Bridge...
start "CAS BRIDGE" %PYTHON_EXE% cas_bridge.py

echo Starting CAS Brain...
start "CAS BRAIN" %PYTHON_EXE% cas_brain.py

echo Systems online.
timeout /t 5