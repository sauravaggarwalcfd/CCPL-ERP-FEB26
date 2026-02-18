@echo off
title CCPL ERP

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "BACKEND_DIR=%ROOT%\backend"
set "FRONTEND_DIR=%ROOT%\frontend"
set "VENV_DIR=%BACKEND_DIR%\venv_win"

echo Starting Backend...
if not exist "%VENV_DIR%" (
    python -m venv "%VENV_DIR%"
    call "%VENV_DIR%\Scripts\activate.bat"
    pip install -r "%BACKEND_DIR%\requirements.txt" --quiet
) else (
    call "%VENV_DIR%\Scripts\activate.bat"
)
start "CCPL-Backend" cmd /k "title CCPL Backend & cd /d "%BACKEND_DIR%" & call "%VENV_DIR%\Scripts\activate.bat" & python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting Frontend...
if not exist "%FRONTEND_DIR%\node_modules" (
    pushd "%FRONTEND_DIR%"
    call npm install
    popd
)
start "CCPL-Frontend" cmd /k "title CCPL Frontend & cd /d "%FRONTEND_DIR%" & npm run dev -- --strictPort"

echo.
echo  Backend  : http://localhost:8000
echo  Frontend : http://localhost:8085
echo.
pause
