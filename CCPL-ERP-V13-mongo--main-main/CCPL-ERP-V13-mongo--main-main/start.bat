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
    echo     Selecting Python version...

    REM Prefer Python 3.12, then 3.11, then 3.10, then default
    set "PYEXE=python"
    py -3.12 --version >nul 2>&1
    if not errorlevel 1 ( set "PYEXE=py -3.12" & goto :create_venv )
    py -3.11 --version >nul 2>&1
    if not errorlevel 1 ( set "PYEXE=py -3.11" & goto :create_venv )
    py -3.10 --version >nul 2>&1
    if not errorlevel 1 ( set "PYEXE=py -3.10" & goto :create_venv )

    :create_venv
    echo     Creating virtual environment with: %PYEXE%
    %PYEXE% -m venv "%VENV_DIR%"
)

echo     Upgrading pip and build tools...
"%PIP%" install --upgrade pip setuptools wheel --quiet

echo     Installing packages...
"%PIP%" install --prefer-binary -r "%BACKEND_DIR%\requirements.txt"
if errorlevel 1 (
    echo.
    echo  ERROR: pip install failed!
    echo.
    echo  Your Python version may be too new (3.14 has limited package support).
    echo  Please install Python 3.12 from: https://www.python.org/downloads/
    echo  Then delete the venv_win folder and run start.bat again.
    echo.
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
