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

# 4. Check database readiness
if [ -n "$DB_NAME" ] || [ "$(echo "$USE_POSTGRES" | tr '[:upper:]' '[:lower:]')" = "true" ]; then
    _pg_host="${DB_HOST:-localhost}"
    _pg_port="${DB_PORT:-5432}"
    echo "[*] PostgreSQL mode detected. Checking connectivity to ${_pg_host}:${_pg_port}..."
    if command -v pg_isready > /dev/null 2>&1; then
        pg_isready -h "$_pg_host" -p "$_pg_port" -t 5
        _pg_ok=$?
    else
        python - <<'PYEOF'
import sys, os
try:
    import psycopg2
    psycopg2.connect(
        dbname=os.environ.get('DB_NAME',''),
        user=os.environ.get('DB_USER',''),
        password=os.environ.get('DB_PASSWORD',''),
        host=os.environ.get('DB_HOST','localhost'),
        port=os.environ.get('DB_PORT','5432'),
        connect_timeout=5,
    ).close()
    print("[OK] PostgreSQL is reachable.")
except Exception as e:
    print(f"[ERROR] Cannot connect to PostgreSQL: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF
        _pg_ok=$?
    fi
    if [ $_pg_ok -ne 0 ]; then
        echo ""
        echo "[ERROR] Cannot reach PostgreSQL at ${_pg_host}:${_pg_port}."
        echo "        Make sure PostgreSQL is running and the following env vars are set:"
        echo "          DB_NAME, DB_USER, DB_PASSWORD, DB_HOST (default: localhost), DB_PORT (default: 5432)"
        echo "        Set USE_POSTGRES=true to activate the PostgreSQL backend."
        exit 1
    fi
else
    echo "[INFO] No DB_NAME / USE_POSTGRES set — using SQLite (default)."
fi

# 5. Run database migrations
echo "[*] Running database migrations..."
python manage.py migrate

# 6. Seed demo accounts & sample data
echo "[*] Seeding demo accounts and sample courses..."
python manage.py seed_data

# 7. Ask to create superuser
echo ""
read -r -p "Would you like to create an additional custom admin account? (y/N): " CREATE_ADMIN
if [[ "$CREATE_ADMIN" =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# 8. Start Django server
echo ""
echo "==================================================="
echo " Server is starting!"
echo " Access your app at: http://127.0.0.1:8000/"
echo " Admin panel:        http://127.0.0.1:8000/admin/"
echo " Press Ctrl+C to stop the server."
echo "==================================================="
echo ""

python manage.py runserver