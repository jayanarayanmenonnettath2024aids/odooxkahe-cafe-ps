@echo off
echo Setting up Odoo Cafe POS project...

echo.
echo [1/3] Creating Python virtual environment...
if not exist "venv\" (
    python -m venv venv
) else (
    echo venv already exists.
)

echo.
echo [2/3] Installing backend dependencies...
call venv\Scripts\activate.bat
pip install -e .

echo.
echo [3/3] Installing frontend dependencies...
cd frontend-odoo
call npm install
cd ..

echo.
if not exist ".env" (
    echo Copying .env.example to .env...
    copy .env.example .env
)

echo.
echo Setup completed successfully!
pause
