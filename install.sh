#!/bin/bash

echo "Starting Parmana 2.0 Installation..."

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Copy .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env created from template. Make sure to edit it and add your API keys!"
fi

echo ""
echo "Installation complete!"
echo "To start the agent:"
echo "1. source .venv/bin/activate"
echo "2. python main.py"
