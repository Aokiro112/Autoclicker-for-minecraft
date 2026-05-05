@echo off
:: ============================================================
::  Minecraft Auto-Clicker  |  SKLauncher Edition
::  One-click installer + launcher
:: ============================================================
title Minecraft Auto-Clicker – Setup

echo ============================================================
echo   Minecraft Auto-Clicker  ^|  SKLauncher Edition
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.  Please install Python 3.10+
    echo         from https://www.python.org/downloads/
    echo         Make sure to tick "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo [1/2] Installing required libraries...
pip install keyboard pywin32 psutil --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [ERROR] pip install failed.  Check your internet connection.
    pause
    exit /b 1
)

echo [2/2] Launching Auto-Clicker...
echo.

:: Run with elevated privileges so keyboard hooks work reliably
powershell -Command "Start-Process python -ArgumentList 'autoclicker.py' -Verb RunAs -WorkingDirectory '%~dp0'"
