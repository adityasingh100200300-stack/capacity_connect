@echo off
setlocal enabledelayedexpansion
title Capacity Connect - Setup & Start

:: Ensure we run from the project root directory
cd /d "%~dp0"

echo ===================================================
echo       Capacity Connect - Automatic Setup
echo ===================================================
echo.

:: 1. Check Python installation
set "PY_CMD="
where python >nul 2>nul
if %ERRORLEVEL% equ 0 set "PY_CMD=python"

if not defined PY_CMD (
    where py >nul 2>nul
    if %ERRORLEVEL% equ 0 set "PY_CMD=py"
)

if not defined PY_CMD (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3 from https://www.python.org/
    echo Make sure to check Add Python to PATH during installation.
    echo.
    pause
    exit /b 1
)

:: 2. Create virtual environment if it does not exist
if not exist ".venv\Scripts\activate.bat" (
    echo [*] Creating virtual environment...
    %PY_CMD% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: 3. Activate virtual environment
echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat

:: 4. Install / Update dependencies
echo [*] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: 5. Run database migrations
echo [*] Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo [ERROR] Database migration failed.
    pause
    exit /b 1
)

:: 6. Optional: Create initial admin superuser
echo.
set /p CREATE_ADMIN="Would you like to create an admin account now? (y/N): "
if /i "!CREATE_ADMIN!"=="y" (
    python manage.py createsuperuser
)

:: 7. Start Django server
echo.
echo ===================================================
echo  Server is starting!
echo  Access your app at: http://127.0.0.1:8000/
echo  Admin panel:        http://127.0.0.1:8000/admin/
echo  Press Ctrl+C to stop the server.
echo ===================================================
echo.

python manage.py runserver

pause
