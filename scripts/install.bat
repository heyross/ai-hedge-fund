@echo off
setlocal enabledelayedexpansion

:: Enable verbose output
set PIP_VERBOSE=1
set PIP_LOG=pip_install.log

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

:: Install packages in stages
echo Installing base requirements...
python -m pip install --upgrade pip setuptools wheel --verbose > pip_install.log 2>&1
if %errorLevel% neq 0 (
    echo Failed to install base requirements. Check pip_install.log for details
    pause
    exit /b 1
)

echo Installing core dependencies...
pip install --verbose psutil python-dotenv >> pip_install.log 2>&1
if %errorLevel% neq 0 (
    echo Failed to install core dependencies. Check pip_install.log for details
    pause
    exit /b 1
)

echo Installing data science packages...
echo Installing numpy...
pip install --verbose "numpy>=1.25.0,<2.0.0" >> pip_install.log 2>&1
if %errorLevel% neq 0 (
    echo Failed to install numpy. Check pip_install.log for details
    pause
    exit /b 1
)

echo Installing matplotlib...
pip install --verbose matplotlib==3.9.2 >> pip_install.log 2>&1
if %errorLevel% neq 0 (
    echo Failed to install matplotlib. Check pip_install.log for details
    pause
    exit /b 1
)

echo Installing pandas...
pip install --verbose pandas==2.2.0 >> pip_install.log 2>&1
if %errorLevel% neq 0 (
    echo Failed to install pandas. Check pip_install.log for details
    pause
    exit /b 1
)

echo Installing API packages...
pip install --verbose fastapi==0.95.1 uvicorn==0.22.0 >> pip_install.log 2>&1
if %errorLevel% neq 0 (
    echo Failed to install API packages. Check pip_install.log for details
    pause
    exit /b 1
)

echo Installing AI packages...
pip install --verbose langchain==0.0.350 langchain-openai==0.0.2 langchain-community==0.0.21 >> pip_install.log 2>&1
if %errorLevel% neq 0 (
    echo Failed to install AI packages. Check pip_install.log for details
    pause
    exit /b 1
)

:: Run the installation script
echo Running installation script...
python "%~dp0install.py" > install_script.log 2>&1
if %errorLevel% neq 0 (
    echo Installation failed. Please check install_script.log for details.
    pause
    exit /b 1
)

echo Installation completed successfully!
pause
