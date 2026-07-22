@echo off
REM Quick setup script for TransitOps backend (Windows)

echo ==========================================
echo TransitOps Backend Setup
echo ==========================================

REM Check Python version
echo Checking Python version...
python --version

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Copy environment file
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo WARNING: Please update .env file with your database credentials!
)

echo.
echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo Next steps:
echo 1. Update .env file with your database credentials
echo 2. Create PostgreSQL database
echo 3. Run migrations: alembic upgrade head
echo 4. Seed data: python seed_data.py
echo 5. Start server: uvicorn app.main:app --reload
echo.
pause
