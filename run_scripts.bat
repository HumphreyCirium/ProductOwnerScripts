@echo off
REM Product Owner Scripts Runner - Batch Wrapper
REM This batch file allows you to run the Python script runner from Windows Explorer

setlocal EnableDelayedExpansion

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Set window title
title Product Owner Scripts Runner

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Display header
echo.
echo ================================================================================
echo 🐍 PRODUCT OWNER SCRIPTS RUNNER
echo ================================================================================
echo.
echo Current directory: %CD%
echo Python version:
python --version
echo.

REM Check if script_runner.py exists
if not exist "script_runner.py" (
    echo ❌ ERROR: script_runner.py not found in current directory
    echo.
    echo Please make sure script_runner.py is in the same folder as this batch file.
    echo.
    pause
    exit /b 1
)

REM Check if config.ini exists
if not exist "config.ini" (
    echo ⚠️  WARNING: config.ini not found
    echo.
    echo Some scripts may require configuration. Please create config.ini
    echo based on config.example.json if needed.
    echo.
    echo Press any key to continue anyway...
    pause >nul
    echo.
)

REM Run the Python script runner
echo 🚀 Starting Python Script Runner...
echo.
python script_runner.py

REM Check the exit code
if errorlevel 1 (
    echo.
    echo ❌ Script runner exited with an error
) else (
    echo.
    echo ✅ Script runner completed successfully
)

echo.
echo ================================================================================
echo Press any key to close this window...
pause >nul