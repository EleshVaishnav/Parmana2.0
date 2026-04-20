Write-Host ""
Write-Host "  ____   _    ____  __  __    _    _   _    _      ____     ___  " -ForegroundColor Blue
Write-Host " |  _ \ / \  |  _ \|  \/  |  / \  | \ | |  / \    |___ \   / _ \ " -ForegroundColor Blue
Write-Host " | |_) / _ \ | |_) | |\/| | / _ \ |  \| | / _ \     __) | | | | |" -ForegroundColor Blue
Write-Host " |  __/ ___ \|  _ <| |  | |/ ___ \| |\  |/ ___ \   / __/ _| |_| |" -ForegroundColor Blue
Write-Host " |_| /_/   \_\_| \_\_|  |_/_/   \_\_| \_/_/   \_\ |_____(_)\___/ " -ForegroundColor Blue
Write-Host ""
Write-Host "Bootstrapping Deep Claw 2.0 Installer..." -ForegroundColor Cyan

# If we are running this via one-liner over the web, clone the repo automatically!
if (-not (Test-Path "setup.py")) {
    Write-Host "Remote execution detected. Cloning repository..." -ForegroundColor Yellow
    git clone https://github.com/EleshVaishnav/DeepClaw2.0.git
    Set-Location -Path "DeepClaw2.0"
}

# Create virtual environment
python -m venv .venv

# Activate it and run interactive setup
& .\.venv\Scripts\Activate.ps1
python setup.py
