@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   CCPL Inventory ERP - Google Sheets
echo ========================================
echo.

REM Get the directory where this bat file lives
set "PROJECT_DIR=%~dp0"

REM ---- Check token.json exists ----
if not exist "D:\CCPL ERP FEB26\token.json" (
    echo [WARNING] token.json not found!
    echo Run "python generate_token.py" in backend\ folder first
    echo to authenticate with Google Sheets.
    echo.
    echo The app will start in DEMO MODE (in-memory only, no persistence).
    echo.
    pause
)

REM ---- Start Backend ----
echo Starting Backend (FastAPI on port 8000)...
cd /d "%PROJECT_DIR%backend"

if not exist "venv_win" (
    echo Creating Python virtual environment...
    python -m venv venv_win
)

start "CCPL-ERP Backend" cmd /k "cd /d "%PROJECT_DIR%backend" && call venv_win\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM ---- Start Frontend ----
echo Starting Frontend (Vite on port 8085)...
cd /d "%PROJECT_DIR%frontend"

if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

start "CCPL-ERP Frontend" cmd /k "cd /d "%PROJECT_DIR%frontend" && npm run dev"

echo.
echo ========================================
echo   Services Starting...
echo ========================================
echo.
echo   Backend API:  http://localhost:8000
echo   API Docs:     http://localhost:8000/docs
echo   Frontend:     http://localhost:8085
echo.
echo   Login:  admin@ccpl.com / Admin@123
echo.
echo   Both services run in separate windows.
echo   Close those windows to stop them.
echo ========================================
echo.
pause
