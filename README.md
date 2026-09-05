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