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
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "BACKEND_DIR=%ROOT%\backend"
set "FRONTEND_DIR=%ROOT%\frontend"
set "VENV_DIR=%BACKEND_DIR%\venv_win"

REM ===================================================
REM  STEP 1 - Sync latest code from GitHub (force overwrite local)
REM ===================================================
echo [1/4] Syncing latest code from GitHub...
cd /d "%ROOT%"
git fetch origin main
git reset --hard origin/main
echo  Code is now up to date with GitHub.
echo.

REM ===================================================
REM  STEP 2 - Backend setup
REM ===================================================
echo [2/4] Setting up Python backend...

if not exist "%VENV_DIR%" (
    echo      Creating virtual environment (first run, please wait)...
    python -m venv "%VENV_DIR%"
    call "%VENV_DIR%\Scripts\activate.bat"
    echo      Installing Python dependencies...
    pip install -r "%BACKEND_DIR%\requirements.txt" --quiet
) else (
    call "%VENV_DIR%\Scripts\activate.bat"
)

echo [3/4] Starting Backend on http://localhost:8000 ...
start "CCPL-Backend" cmd /k "title CCPL Backend & cd /d "%BACKEND_DIR%" & call "%VENV_DIR%\Scripts\activate.bat" & python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM ===================================================
REM  STEP 3 - Frontend setup
REM ===================================================
echo [4/4] Starting Frontend on http://localhost:8085 ...

if not exist "%FRONTEND_DIR%\node_modules" (
    echo      Installing npm packages (first run, please wait)...
    pushd "%FRONTEND_DIR%"
    call npm install
    popd
)

start "CCPL-Frontend" cmd /k "title CCPL Frontend & cd /d "%FRONTEND_DIR%" & npm run dev -- --strictPort"

REM ===================================================
REM  Open browser after servers boot
REM ===================================================
echo.
echo  Waiting 8 seconds for servers to start...
timeout /t 8 /nobreak >nul
start "" "http://localhost:8085"

echo.
echo  ============================================
echo    CCPL ERP is RUNNING
echo.
echo    App       :  http://localhost:8085
echo    API Docs  :  http://localhost:8000/docs
echo.
echo    To STOP: run stop.bat  (or close the two
echo             CMD windows named CCPL-Backend
echo             and CCPL-Frontend)
echo  ============================================
echo.
pause
