@echo off
setlocal

echo ========================================================
echo  Launching Library Book Reservation System
echo ========================================================

cd /d "%~dp0"

if not exist "env\Scripts\activate.bat" (
    echo [ERROR] Virtual environment 'env' not found. Please run setupdev.bat first!
    pause
    exit /b 1
)

echo Starting backend in a separate window (FastAPI on http://127.0.0.1:8000)...
start "Library Backend (FastAPI)" cmd /k "cd /d ""%~dp0"" && call .\env\Scripts\activate.bat && python main.py"

echo Starting frontend in a separate window (React Vite on http://localhost:3000)...
start "Library Frontend (React)" cmd /k "cd /d ""%~dp0frontend"" && npm start"

echo.
echo ========================================================
echo  Both services launched!
echo  - Swagger UI Docs: http://127.0.0.1:8000/docs
echo  - React Frontend:  http://localhost:3000
echo ========================================================
