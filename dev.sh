#!/bin/bash

# Function to handle Ctrl+C
function handle_sigint() {
    echo -e "\nReceived interrupt signal. Stopping development server..."
    exit 1
}

# Set trap for SIGINT (Ctrl+C)
trap handle_sigint INT

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Using existing virtual environment..."
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the development server
echo "Starting development server with auto-restart..."
pip install -r requirements.txt    
# Execute Python script and allow signal propagation
exec python run_dev.py 