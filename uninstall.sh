#!/bin/bash

echo "Uninstalling Deep Claw 2.0 Environment..."

if [ -d ".venv" ]; then
    echo "Removing virtual environment (.venv)..."
    rm -rf .venv
fi

echo "Cleaning up Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} +

echo "Uninstallation complete. Note: Your .env configurations and chroma_db memory were securely kept."
