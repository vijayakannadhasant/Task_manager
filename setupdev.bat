@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo  Library Book Reservation System - Environment Setup
echo ========================================================

cd /d "%~dp0"

echo.
echo [1/5] Checking Python Virtual Environment...
if not exist "env\Scripts\activate.bat" (
    echo Creating virtual environment at .\env ...
    python -m venv env
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create python virtual environment. Please ensure Python 3.10+ is installed.
        exit /b %errorlevel%
    )
) else (
    echo Existing virtual environment found.
)

echo.
echo [2/5] Activating virtual environment and installing backend dependencies...
call env\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend requirements.
    exit /b %errorlevel%
)

echo.
echo [3/5] Applying Alembic database migrations...
alembic upgrade head
if %errorlevel% neq 0 (
    echo [ERROR] Alembic database migration failed.
    exit /b %errorlevel%
)

echo.
echo [4/5] Checking generated SDK installation...
if exist "library_sdk\setup.py" (
    pip install -e ./library_sdk
)

echo.
echo [5/5] Installing Frontend NPM dependencies...
if not exist "frontend" (
    echo [ERROR] frontend directory not found.
    exit /b 1
)

cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install frontend npm packages.
    cd ..
    exit /b %errorlevel%
)
cd ..

echo.
echo ========================================================
echo  Setup Complete!
echo  To seed sample data:  python scripts\seed_db.py
echo  To run tests:         pytest
echo  To launch app:        runapplication.bat
echo ========================================================
