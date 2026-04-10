Write-Host "Starting Parmana 2.0 Installation..." -ForegroundColor Cyan

# Create virtual environment
Write-Host "Creating Virtual Environment..."
python -m venv .venv

# Activate it and install requirements
Write-Host "Installing dependencies..."
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Copy .env file if it doesn't exist
if (-Not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host ".env created from template. Make sure to edit it and add your API keys!" -ForegroundColor Yellow
}

Write-Host "`nInstallation complete!" -ForegroundColor Green
Write-Host "To start the agent:"
Write-Host "1. .\.venv\Scripts\Activate.ps1"
Write-Host "2. python main.py"
