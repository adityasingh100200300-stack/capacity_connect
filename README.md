# Capacity Connect

A comprehensive capacity and competency management platform built with Django and Django REST Framework.

---

## 🚀 Quick Start (1-Step Automatic Setup)

Once you clone the repository

### 🪟 Windows Users (Easiest)
- **Option A (No terminal needed):** Just **double-click** `setup.bat` in File Explorer.
- **Option B (PowerShell):**
  ```powershell
  .\setup.bat
  ```
- **Option C (Command Prompt / CMD):**
  ```cmd
  setup.bat
  ```

---

### 🍎 macOS & 🐧 Linux Users
Open your terminal inside the project directory and run:
```bash
bash setup.sh
```
*(No `chmod` required!)*

---

## 🛠️ What the Setup Script Automates:
1. **Checks for Python** (Python 3.10+ recommended).
2. **Creates a virtual environment** (`.venv`) if one does not exist.
3. **Activates the virtual environment**.
4. **Installs all required dependencies** from `requirements.txt`.
5. **Applies database migrations** (`python manage.py migrate`).
6. **Prompts you to create an admin/superuser** (optional).
7. **Starts the local development server** at `http://127.0.0.1:8000/`.

---

## 🗄️ Database Setup

The project supports **two database backends**. The default is SQLite (zero config).
Switch to PostgreSQL by setting environment variables before running the setup script.

### Option A — SQLite (default, no configuration needed)

If you don't set any database environment variables the app automatically uses SQLite.
Perfect for local development; the `db.sqlite3` file is created in the project root.

> **Not recommended for production.** Use PostgreSQL for any shared/staging/production environment.

---

### Option B — PostgreSQL

#### 1. Install PostgreSQL
- **macOS:** `brew install postgresql@16 && brew services start postgresql@16`
- **Ubuntu/Debian:** `sudo apt install postgresql-16`
- **Windows:** Download from https://www.postgresql.org/download/windows/
- **Docker (quickest):** see the Docker section below.

#### 2. Create a database and user

```sql
-- run as the postgres superuser (psql -U postgres)
CREATE DATABASE capacity_connect;
CREATE USER capacity_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE capacity_connect TO capacity_user;
-- PostgreSQL 15+: also grant schema privileges
\c capacity_connect
GRANT ALL ON SCHEMA public TO capacity_user;
```

#### 3. Set environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `USE_POSTGRES` | No (optional gate) | `false` | Set `true` to activate PostgreSQL |
| `DB_NAME` | Yes | — | Database name (e.g. `capacity_connect`) |
| `DB_USER` | Yes | — | PostgreSQL username |
| `DB_PASSWORD` | Yes | — | PostgreSQL password |
| `DB_HOST` | No | `localhost` | Postgres server host |
| `DB_PORT` | No | `5432` | Postgres server port |

Copy `.env.example` → `.env` and fill in your values, **or** export variables in your shell:

```bash
# bash / zsh
export USE_POSTGRES=true
export DB_NAME=capacity_connect
export DB_USER=capacity_user
export DB_PASSWORD=your_secure_password
```

```powershell
# PowerShell
$env:USE_POSTGRES = "true"
$env:DB_NAME      = "capacity_connect"
$env:DB_USER      = "capacity_user"
$env:DB_PASSWORD  = "your_secure_password"
```

#### 4. Run migrations

```bash
python manage.py migrate
```

---

### 🐳 Optional: Docker Compose (quickest local Postgres)

If you don't want to install Postgres locally, spin it up with Docker:

```bash
# one-time: pull and start a Postgres 16 container
docker run -d \
  --name capacity_postgres \
  -e POSTGRES_DB=capacity_connect \
  -e POSTGRES_USER=capacity_user \
  -e POSTGRES_PASSWORD=your_secure_password \
  -p 5432:5432 \
  postgres:16

# then set the env vars and run the setup script as usual
```

> A `docker-compose.yml` is not yet included in this repository.
> If you'd like one added, open an issue or ask the project maintainer.