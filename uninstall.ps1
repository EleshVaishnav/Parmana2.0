Write-Host "Uninstalling Deep Claw 2.0 Environment..." -ForegroundColor Yellow

if (Test-Path ".venv") {
    Write-Host "Removing virtual environment (.venv)..."
    Remove-Item -Recurse -Force .venv
}

Write-Host "Cleaning up Python cache files..."
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force

Write-Host "Uninstallation complete. Note: Your .env configurations and chroma_db memory were securely kept." -ForegroundColor Green
