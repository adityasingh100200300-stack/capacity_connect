@echo off
title Capacity Connect - Setup & Start

:: Ensure we run from the project root directory
cd /d "%~dp0"

echo ===================================================
echo       Capacity Connect - Automatic Setup
echo ===================================================
echo.

set "VENV_DIR=%~dp0.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

:: 1. Check if virtual environment already exists
if exist "%VENV_PY%" goto :VENV_READY

set "PY_CMD="
where python >nul 2>nul
if %ERRORLEVEL% equ 0 set "PY_CMD=python"
if not defined PY_CMD (
    where py >nul 2>nul
    if %ERRORLEVEL% equ 0 set "PY_CMD=py"
)
if not defined PY_CMD (
    if exist "%LocalAppData%\Programs\Python\Python313\python.exe" (
        set "PY_CMD=%LocalAppData%\Programs\Python\Python313\python.exe"
    )
)

if not defined PY_CMD (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3 from https://www.python.org/
    echo Make sure to check Add Python to PATH during installation.
    echo.
    pause
    exit /b 1
)

echo [*] Creating virtual environment (.venv)...
"%PY_CMD%" -m venv .venv
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

:VENV_READY
:: 2. Activate virtual environment
if exist "%VENV_DIR%\Scripts\activate.bat" call "%VENV_DIR%\Scripts\activate.bat"

:: 3. Install / Update dependencies
echo [*] Installing dependencies from requirements.txt...
"%VENV_PY%" -m pip install -r requirements.txt
if %ERRORLEVEL% equ 0 goto :DEPS_OK

echo.
echo [WARNING] Full requirements.txt install encountered an issue.
echo [*] Attempting fallback install of core dependencies (SQLite support)...
"%VENV_PY%" -m pip install Django==6.1.1 Pillow PyOTP sqlparse tzdata asgiref
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [INFO] Core dependencies installed successfully.

:DEPS_OK
:: 4. Check database readiness
set "_PG_MODE="
if defined DB_NAME set "_PG_MODE=1"
if /i "%USE_POSTGRES%"=="true" set "_PG_MODE=1"
if /i "%USE_POSTGRES%"=="1" set "_PG_MODE=1"
if /i "%USE_POSTGRES%"=="yes" set "_PG_MODE=1"

if not defined _PG_MODE goto :USE_SQLITE

set "_PG_HOST=%DB_HOST%"
if not defined _PG_HOST set "_PG_HOST=localhost"
set "_PG_PORT=%DB_PORT%"
if not defined _PG_PORT set "_PG_PORT=5432"

echo [*] PostgreSQL mode detected. Checking connectivity to %_PG_HOST%:%_PG_PORT%...
"%VENV_PY%" -c "import sys, os, psycopg2; psycopg2.connect(dbname=os.environ.get('DB_NAME',''), user=os.environ.get('DB_USER',''), password=os.environ.get('DB_PASSWORD',''), host=os.environ.get('DB_HOST','localhost'), port=os.environ.get('DB_PORT','5432'), connect_timeout=5).close(); print('[OK] PostgreSQL is reachable.')"
if %ERRORLEVEL% equ 0 goto :RUN_MIGRATIONS

echo.
echo [ERROR] Cannot connect to PostgreSQL at %_PG_HOST%:%_PG_PORT!.
echo         Make sure PostgreSQL is running and the following env vars are set:
echo           DB_NAME, DB_USER, DB_PASSWORD
echo           DB_HOST  (default: localhost)
echo           DB_PORT  (default: 5432)
echo         Or unset USE_POSTGRES/DB_NAME to use SQLite (default).
pause
exit /b 1

:USE_SQLITE
echo [INFO] No DB_NAME / USE_POSTGRES set -- using SQLite (default).

:RUN_MIGRATIONS
:: 5. Run database migrations
echo [*] Running database migrations...
"%VENV_PY%" manage.py migrate
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Database migration failed.
    echo Try running: "%VENV_PY%" manage.py migrate --traceback
    pause
    exit /b 1
)

:: 6. Optional: Create initial admin superuser
echo.
set "CREATE_ADMIN="
set /p CREATE_ADMIN="Would you like to create an admin account now? (y/N): "
if /i "%CREATE_ADMIN%"=="y" "%VENV_PY%" manage.py createsuperuser

:: 7. Start Django server
echo.
echo ===================================================
echo  Server is starting!
echo  Local PC access:     http://127.0.0.1:8000/
echo  Mobile / LAN access: http://0.0.0.0:8000/
echo  (Use your PC's Wi-Fi IP on your phone, e.g. http://10.134.208.132:8000/)
echo  Admin panel:         http://127.0.0.1:8000/admin/
echo  Press Ctrl+C to stop the server.
echo ===================================================
echo.

"%VENV_PY%" manage.py runserver 0.0.0.0:8000

pause
