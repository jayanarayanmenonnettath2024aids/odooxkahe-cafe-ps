@echo off
echo Starting servers for Odoo Cafe POS...

echo Starting Backend Server...
start "Cafe POS Backend" cmd /k "call venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000 --host 0.0.0.0"

echo Starting Frontend Server...
start "Cafe POS Frontend" cmd /k "cd frontend-odoo && npm run dev"

echo Both servers are starting in separate windows.
