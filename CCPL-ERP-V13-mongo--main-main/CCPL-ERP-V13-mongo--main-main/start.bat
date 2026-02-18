@echo off
setlocal enabledelayedexpansion
title CCPL ERP Launcher

echo.
echo  ============================================
echo    CCPL Inventory ERP  -  MongoDB Atlas
echo  ============================================
echo.

REM ---- Resolve project root (where this .bat lives) ----
set "ROOT=%~dp0"
REM Remove trailing backslash
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "BACKEND_DIR=%ROOT%\backend"
set "FRONTEND_DIR=%ROOT%\frontend"
set "VENV_DIR=%BACKEND_DIR%\venv_win"

REM ===================================================
REM  BACKEND
REM ===================================================
echo [1/3] Setting up Python backend...

if not exist "%VENV_DIR%" (
    echo      Creating virtual environment (first run)...
    python -m venv "%VENV_DIR%"
    call "%VENV_DIR%\Scripts\activate.bat"
    echo      Installing Python dependencies...
    pip install -r "%BACKEND_DIR%\requirements.txt" --quiet
) else (
    call "%VENV_DIR%\Scripts\activate.bat"
)

echo [2/3] Starting Backend on http://localhost:8000 ...
start "CCPL-Backend" cmd /k "title CCPL Backend & cd /d "%BACKEND_DIR%" & call "%VENV_DIR%\Scripts\activate.bat" & python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM ===================================================
REM  FRONTEND
REM ===================================================
echo [3/3] Starting Frontend on http://localhost:8085 ...

if not exist "%FRONTEND_DIR%\node_modules" (
    echo      Installing npm packages (first run)...
    pushd "%FRONTEND_DIR%"
    call npm install
    popd
)

start "CCPL-Frontend" cmd /k "title CCPL Frontend & cd /d "%FRONTEND_DIR%" & npm run dev -- --strictPort"

REM ===================================================
REM  OPEN BROWSER  (wait a few seconds for servers to boot)
REM ===================================================
echo.
echo  Waiting for servers to start...
timeout /t 6 /nobreak >nul
start "" "http://localhost:8085"

echo.
echo  ============================================
echo    Both services are running!
echo.
echo    Frontend  :  http://localhost:8085
echo    Backend   :  http://localhost:8000
echo    API Docs  :  http://localhost:8000/docs
echo.
echo    Login     :  admin@ccpl.com / Admin@123
echo.
echo    Close the two CMD windows to stop servers.
echo  ============================================
echo.
pause
