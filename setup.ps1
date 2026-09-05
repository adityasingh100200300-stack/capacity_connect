# Capacity Connect - Automated Setup Script for Windows PowerShell
$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "      Capacity Connect - Automatic Setup" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
$pyCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pyCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pyCmd = "py"
} else {
    Write-Host "[ERROR] Python is not installed or not found in PATH." -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/ and check 'Add Python to PATH'." -ForegroundColor Yellow
    Exit 1
}

# 2. Virtual Environment
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "[*] Creating virtual environment (.venv)..." -ForegroundColor Cyan
    & $pyCmd -m venv .venv
}

# 3. Activate
Write-Host "[*] Activating virtual environment..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

# 4. Install dependencies
Write-Host "[*] Installing dependencies from requirements.txt..." -ForegroundColor Cyan
pip install -r requirements.txt

# 5. Run migrations
Write-Host "[*] Running database migrations..." -ForegroundColor Cyan
python manage.py migrate

# 6. Admin user prompt
Write-Host ""
$createAdmin = Read-Host "Would you like to create an admin account now? (y/N)"
if ($createAdmin -match '^[Yy]') {
    python manage.py createsuperuser
}

# 7. Start server
Write-Host ""
Write-Host "===================================================" -ForegroundColor Green
Write-Host " Server is starting!" -ForegroundColor Green
Write-Host " Access your app at: http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host " Admin panel:        http://127.0.0.1:8000/admin/" -ForegroundColor Green
Write-Host " Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Green
Write-Host ""

python manage.py runserver
