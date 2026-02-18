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
REM  STEP 1 - Sync latest code from GitHub
REM ===================================================
echo [1/4] Syncing latest code from GitHub...
cd /d "%ROOT%"
git fetch origin main
git reset --hard origin/main
echo  Code is now up to date with GitHub.
echo.

REM Re-apply paths after reset (file may have been overwritten)
set "BACKEND_DIR=%ROOT%\backend"
set "FRONTEND_DIR=%ROOT%\frontend"
set "VENV_DIR=%BACKEND_DIR%\venv_win"

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
REM  Wait until port 8085 is actually listening, then open browser
REM ===================================================
echo.
echo  Waiting for frontend to be ready (checking port 8085)...
set /a TRIES=0

:POLL_LOOP
timeout /t 2 /nobreak >nul
set /a TRIES+=1
powershell -NoProfile -Command "try { $t = New-Object System.Net.Sockets.TcpClient('localhost',8085); $t.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 goto BROWSER_OPEN
if %TRIES% GEQ 30 goto BROWSER_OPEN
echo  Still starting... (%TRIES%/30)
goto POLL_LOOP

:BROWSER_OPEN
echo  Frontend is ready! Opening browser...
start "" "http://localhost:8085"

echo.
echo  ============================================
echo    CCPL ERP is RUNNING
echo.
echo    App       :  http://localhost:8085
echo    API Docs  :  http://localhost:8000/docs
echo.
echo    To STOP: run stop.bat
echo  ============================================
echo.
pause
