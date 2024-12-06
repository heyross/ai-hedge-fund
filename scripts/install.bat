@echo off
setlocal enabledelayedexpansion

:: Check for administrative privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script requires administrative privileges.
    echo Please run this script as Administrator.
    pause
    exit /b 1
)

:: Check if Python is installed
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.10 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2 delims=." %%I in ('python -c "import sys; print(sys.version.split()[0])"') do set PYTHON_VERSION=%%I
if %PYTHON_VERSION% LSS 10 (
    echo Python version 3.10 or higher is required.
    echo Current version: %PYTHON_VERSION%
    pause
    exit /b 1
)

:: Create and activate virtual environment if it doesn't exist
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    if !errorLevel! neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
call .venv\Scripts\activate.bat
if %errorLevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install required packages
echo Installing required packages...
python -m pip install --upgrade pip
pip install psutil
if %errorLevel% neq 0 (
    echo Failed to install required packages.
    pause
    exit /b 1
)

:: Run the installation script
echo Running installation script...
python scripts\install.py
if %errorLevel% neq 0 (
    echo Installation failed. Please check the error messages above.
    pause
    exit /b 1
)

echo Installation completed successfully!
pause
