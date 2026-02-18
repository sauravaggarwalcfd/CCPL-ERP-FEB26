@echo off
title CCPL ERP

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "BACKEND_DIR=%ROOT%\backend"
set "FRONTEND_DIR=%ROOT%\frontend"
set "VENV_DIR=%BACKEND_DIR%\venv_win"
set "PIP=%VENV_DIR%\Scripts\pip.exe"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"

echo.
echo [1/3] Setting up Python environment...
if not exist "%VENV_DIR%" (
    echo     Creating virtual environment...
    python -m venv "%VENV_DIR%"
)

echo     Installing/updating packages from requirements.txt...
"%PIP%" install -r "%BACKEND_DIR%\requirements.txt"
if errorlevel 1 (
    echo.
    echo  ERROR: pip install failed! See errors above.
    pause
    exit /b 1
)

echo.
echo [2/3] Starting Backend on port 8000...
start "CCPL-Backend" cmd /k "title CCPL Backend & cd /d "%BACKEND_DIR%" & "%PYTHON%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo [3/3] Starting Frontend on port 8085...
if not exist "%FRONTEND_DIR%\node_modules" (
    echo     Installing npm packages...
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
