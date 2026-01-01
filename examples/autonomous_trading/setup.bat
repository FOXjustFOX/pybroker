@echo off
REM Quick Start Script for Autonomous Trading Setup (Windows)
REM This script helps you get started with PyBroker autonomous trading

echo ==================================================
echo PyBroker Autonomous Trading Setup
echo ==================================================
echo.

REM Check Python installation
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org/
    pause
    exit /b 1
)

python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist "venv" (
    echo WARNING: Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    echo Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
echo Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env >nul
    echo .env file created
    echo.
    echo WARNING: Edit .env file with your Alpaca API credentials
    echo Get credentials from: https://alpaca.markets/
    echo.
) else (
    echo WARNING: .env file already exists. Not overwriting.
    echo.
)

REM Create cache directories
echo Creating cache directories...
if not exist "data_cache" mkdir data_cache
if not exist "indicator_cache" mkdir indicator_cache
echo Cache directories created
echo.

REM Test installation
echo Testing installation...
python -c "import pybroker; print('PyBroker version:', pybroker.__version__)" 2>nul
if errorlevel 1 (
    echo ERROR: PyBroker installation failed
    pause
    exit /b 1
)
echo.

REM Summary
echo ==================================================
echo Setup Complete!
echo ==================================================
echo.
echo Next Steps:
echo.
echo 1. Edit .env file with your Alpaca credentials:
echo    notepad .env
echo.
echo 2. Run a backtest to verify setup:
echo    python strategy.py
echo.
echo 3. Start autonomous trading (paper mode):
echo    python run_autonomous.py
echo.
echo For detailed documentation, see:
echo - README.md in this directory
echo - AUTONOMOUS_TRADING_SETUP.md in repository root
echo.
echo WARNING: Always start with paper trading!
echo.
pause
