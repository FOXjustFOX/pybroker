#!/bin/bash
# Quick Start Script for Autonomous Trading Setup
# This script helps you get started with PyBroker autonomous trading

set -e  # Exit on error

echo "=================================================="
echo "PyBroker Autonomous Trading Setup"
echo "=================================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "❌ Python 3.9 or higher is required. You have Python $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your Alpaca API credentials"
    echo "   Get credentials from: https://alpaca.markets/"
    echo ""
else
    echo "⚠️  .env file already exists. Not overwriting."
    echo ""
fi

# Create cache directories
echo "Creating cache directories..."
mkdir -p data_cache indicator_cache
echo "✓ Cache directories created"
echo ""

# Test installation
echo "Testing installation..."
if python -c "import pybroker; print('PyBroker version:', pybroker.__version__)" 2>/dev/null; then
    echo "✓ PyBroker installed successfully"
else
    echo "❌ PyBroker installation failed"
    exit 1
fi
echo ""

# Summary
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Edit .env file with your Alpaca credentials:"
echo "   nano .env"
echo ""
echo "2. Run a backtest to verify setup:"
echo "   python strategy.py"
echo ""
echo "3. Start autonomous trading (paper mode):"
echo "   python run_autonomous.py"
echo ""
echo "For detailed documentation, see:"
echo "- README.md in this directory"
echo "- AUTONOMOUS_TRADING_SETUP.md in repository root"
echo ""
echo "⚠️  Remember: Always start with paper trading!"
echo ""
