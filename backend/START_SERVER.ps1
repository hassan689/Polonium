# PowerShell script to start the backend server
# Run this from the backend directory

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "Create a .env file with required configuration." -ForegroundColor Yellow
    Write-Host "See ENV_SETUP.md for details." -ForegroundColor Yellow
    Write-Host ""
}

# Start the server
Write-Host "Starting backend server..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000





