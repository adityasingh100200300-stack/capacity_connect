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
$venvPy = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "[*] Creating virtual environment (.venv)..." -ForegroundColor Cyan
    & $pyCmd -m venv .venv
}

# 3. Activate (if script allowed)
if (Test-Path ".venv\Scripts\Activate.ps1") {
    try {
        & .\.venv\Scripts\Activate.ps1
    } catch {
        Write-Host "[INFO] Continuing using direct virtualenv python..." -ForegroundColor Gray
    }
}

# 4. Install dependencies
Write-Host "[*] Installing dependencies from requirements.txt..." -ForegroundColor Cyan
try {
    & $venvPy -m pip install -r requirements.txt
} catch {
    Write-Host "[WARNING] Full install failed. Trying core dependencies..." -ForegroundColor Yellow
    & $venvPy -m pip install Django==6.1.1 Pillow PyOTP sqlparse tzdata asgiref
}

# 5. Check database readiness
$pgMode = ($env:DB_NAME -ne $null -and $env:DB_NAME -ne '') -or
          ($env:USE_POSTGRES -match '^(true|1|yes)$')

if ($pgMode) {
    $pgHost = if ($env:DB_HOST) { $env:DB_HOST } else { 'localhost' }
    $pgPort = if ($env:DB_PORT) { $env:DB_PORT } else { '5432' }
    Write-Host "[*] PostgreSQL mode detected. Checking connectivity to ${pgHost}:${pgPort}..." -ForegroundColor Cyan
    $probeScript = @"
import sys, os
try:
    try:
        import psycopg2 as pg
    except ImportError:
        import psycopg as pg
    pg.connect(
        dbname=os.environ.get('DB_NAME',''),
        user=os.environ.get('DB_USER',''),
        password=os.environ.get('DB_PASSWORD',''),
        host=os.environ.get('DB_HOST','localhost'),
        port=os.environ.get('DB_PORT','5432'),
        connect_timeout=5,
    ).close()
    print('[OK] PostgreSQL is reachable.')
except Exception as e:
    print(f'[ERROR] Cannot connect to PostgreSQL: {e}', file=sys.stderr)
    sys.exit(1)
"@
    & $venvPy -c $probeScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "" 
        Write-Host "[ERROR] Cannot reach PostgreSQL at ${pgHost}:${pgPort}." -ForegroundColor Red
        Write-Host "        Make sure PostgreSQL is running and set these environment variables:" -ForegroundColor Yellow
        Write-Host "          `$env:DB_NAME     = 'capacity_connect'" -ForegroundColor Yellow
        Write-Host "          `$env:DB_USER     = 'your_db_user'" -ForegroundColor Yellow
        Write-Host "          `$env:DB_PASSWORD = 'your_password'" -ForegroundColor Yellow
        Write-Host "          `$env:DB_HOST     = 'localhost'  # (optional, default: localhost)" -ForegroundColor Yellow
        Write-Host "          `$env:DB_PORT     = '5432'       # (optional, default: 5432)" -ForegroundColor Yellow
        Write-Host "          `$env:USE_POSTGRES = 'true'      # (activates PostgreSQL backend)" -ForegroundColor Yellow
        Exit 1
    }
} else {
    Write-Host "[INFO] No DB_NAME / USE_POSTGRES set - using SQLite (default)." -ForegroundColor Gray
}

# 6. Run migrations
Write-Host "[*] Running database migrations..." -ForegroundColor Cyan
& $venvPy manage.py migrate

# 7. Seed demo accounts & sample data
Write-Host "[*] Seeding demo accounts and sample courses..." -ForegroundColor Cyan
if (Test-Path "fixtures\demo_data.json") {
    & $venvPy manage.py loaddata fixtures\demo_data.json
}
& $venvPy manage.py seed_data

# 8. Admin user prompt
Write-Host ""
$createAdmin = Read-Host "Would you like to create an additional custom admin account? (y/N)"
if ($createAdmin -match '^[Yy]') {
    & $venvPy manage.py createsuperuser
}

# 9. Start server
Write-Host ""
Write-Host "===================================================" -ForegroundColor Green
Write-Host " Server is starting!" -ForegroundColor Green
Write-Host " Access your app at: http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host " Admin panel:        http://127.0.0.1:8000/admin/" -ForegroundColor Green
Write-Host " Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Green
Write-Host ""

& $venvPy manage.py runserver
