#!/bin/bash

echo "Musical Bingo Maker - Environment Setup"
echo "====================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3 from your package manager or https://python.org/downloads/"
    exit 1
fi

echo "Python found!"
python3 --version

echo ""
echo "Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf .venv
fi

python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo ""
echo "Activating virtual environment..."
source .venv/bin/activate

echo ""
echo "Installing dependencies from requirements.txt..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "Setup completed successfully!"
echo ""
echo "To run the musical bingo maker:"
echo "1. Run: source .venv/bin/activate"
echo "2. Then run: python musical-bingo-maker.py"
echo ""
echo "Or directly run: .venv/bin/python musical-bingo-maker.py"