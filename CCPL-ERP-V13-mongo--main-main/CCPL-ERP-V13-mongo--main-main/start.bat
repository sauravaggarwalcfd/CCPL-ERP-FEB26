@echo off
setlocal enabledelayedexpansion
title CCPL ERP

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "BACKEND_DIR=%ROOT%\backend"
set "FRONTEND_DIR=%ROOT%\frontend"
set "VENV_DIR=%BACKEND_DIR%\venv_win"
set "PIP=%VENV_DIR%\Scripts\pip.exe"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"

echo.
echo  ============================================
echo    CCPL Inventory ERP
echo  ============================================
echo.

REM ===== Git Sync (only if this is a git repo) =====
if exist "%ROOT%\.git" (
    echo Syncing latest code from GitHub...
    cd /d "%ROOT%"
    git fetch origin main
    if not errorlevel 1 (
        git reset --hard origin/main
        echo Done.
    ) else (
        echo [WARN] Git sync failed - using existing local files.
    )
    echo.
)

REM ===== Select Python version (OUTSIDE if block to avoid scoping bug) =====
echo [1/3] Setting up Python environment...

set "PYEXE=python"

py -3.12 --version >nul 2>&1
if not errorlevel 1 set "PYEXE=py -3.12"
if "!PYEXE!"=="py -3.12" goto :have_python

py -3.11 --version >nul 2>&1
if not errorlevel 1 set "PYEXE=py -3.11"
if "!PYEXE!"=="py -3.11" goto :have_python

py -3.10 --version >nul 2>&1
if not errorlevel 1 set "PYEXE=py -3.10"

:have_python
echo     Python: %PYEXE%

REM ===== Create venv if missing =====
if not exist "%VENV_DIR%" (
    echo     Creating virtual environment...
    %PYEXE% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo.
        echo  ERROR: Failed to create virtual environment!
        echo  Make sure Python is installed correctly.
        pause
        exit /b 1
    )
)

REM ===== Install packages =====
echo     Upgrading pip...
"%PIP%" install --upgrade pip setuptools wheel --quiet

echo     Installing packages...
"%PIP%" install --prefer-binary -r "%BACKEND_DIR%\requirements.txt"
if errorlevel 1 (
    echo.
    echo  ERROR: Package install failed! See errors above.
    pause
    exit /b 1
)

REM ===== Start Backend =====
echo.
echo [2/3] Starting Backend on port 8000...
start "CCPL-Backend" cmd /k "title CCPL Backend & cd /d "%BACKEND_DIR%" & "%PYTHON%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM ===== Start Frontend =====
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
