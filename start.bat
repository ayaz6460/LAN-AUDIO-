@echo off
title LAN Audio Streamer
cd /d "%~dp0"

echo.
echo  ========================================
echo   LAN Audio Streamer
echo  ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed or not in PATH
    echo  Please install Python from https://python.org
    pause
    exit /b 1
)

:: Check if dependencies are installed, if not install them
python -c "import aiohttp, pyaudiowpatch" >nul 2>&1
if errorlevel 1 (
    echo  Installing dependencies...
    pip install -r requirements.txt
    echo.
)

echo  Starting server...
echo.
python server.py

pause
