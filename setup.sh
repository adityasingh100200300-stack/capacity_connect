#!/usr/bin/env bash
# Capacity Connect - Automated Setup Script for Linux / macOS

set -e

# Change to the script's directory
cd "$(dirname "$0")"

echo "==================================================="
echo "      Capacity Connect - Automatic Setup"
echo "==================================================="
echo ""

# Find available python command
if command -v python3 >/dev/null 2>&1; then
    PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PY_CMD="python"
else
    echo "[ERROR] Python is not installed or not in your PATH."
    echo "Please install Python 3 (https://www.python.org/)."
    exit 1
fi

# 1. Create virtual environment if missing
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment (.venv)..."
    $PY_CMD -m venv .venv
fi

# 2. Activate virtual environment
echo "[*] Activating virtual environment..."
source .venv/bin/activate

# 3. Install dependencies
echo "[*] Installing dependencies..."
pip install -r requirements.txt

# 4. Run database migrations
echo "[*] Running database migrations..."
python manage.py migrate

# 5. Ask to create superuser
echo ""
read -r -p "Would you like to create an admin account now? (y/N): " CREATE_ADMIN
if [[ "$CREATE_ADMIN" =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# 6. Start Django server
echo ""
echo "==================================================="
echo " Server is starting!"
echo " Access your app at: http://127.0.0.1:8000/"
echo " Admin panel:        http://127.0.0.1:8000/admin/"
echo " Press Ctrl+C to stop the server."
echo "==================================================="
echo ""

python manage.py runserver