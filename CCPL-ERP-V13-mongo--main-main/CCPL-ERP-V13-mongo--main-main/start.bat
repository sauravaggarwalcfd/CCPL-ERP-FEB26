@echo off
setlocal enabledelayedexpansion
title CCPL ERP

REM ============================================================
REM   CONFIGURATION
REM ============================================================
set "REPO_URL=https://github.com/AjayKumarMadaka573/CCPL-ERP-FEB26.git"
set "BRANCH=main"

REM ===== Detect which system this is =====
set "DEPLOY_DIR_1=C:\Users\ABC\OneDrive\Desktop\CCPL-ERP-FEB26-main"
set "DEPLOY_DIR_2=D:\CCPL-ERP-FEB26-main"

REM ===== Pick primary deploy dir based on what exists =====
if exist "D:\" (
    set "DEPLOY_DIR=%DEPLOY_DIR_2%"
    echo  [SYS] D: drive detected - primary: %DEPLOY_DIR_2%
) else (
    set "DEPLOY_DIR=%DEPLOY_DIR_1%"
    echo  [SYS] Using Desktop: %DEPLOY_DIR_1%
)

REM ===== Paths inside deploy dir =====
set "PROJECT_DIR=%DEPLOY_DIR%\CCPL-ERP-V13-mongo--main-main\CCPL-ERP-V13-mongo--main-main"
set "BACKEND_DIR=%PROJECT_DIR%\backend"
set "FRONTEND_DIR=%PROJECT_DIR%\frontend"
set "VENV_DIR=%BACKEND_DIR%\venv_win"
set "PIP=%VENV_DIR%\Scripts\pip.exe"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"

REM ===== Handle command-line arguments =====
if /i "%~1"=="stop"    goto :do_stop
if /i "%~1"=="restart" goto :do_restart
if /i "%~1"=="status"  goto :do_status
if /i "%~1"=="logs"    goto :do_logs

REM ===== Default: pull + start =====
goto :do_start

REM ============================================================
REM   PULL LATEST - Clone or pull fresh code to ALL locations
REM ============================================================
:do_pull
echo.
echo  ===========================================
echo    Syncing latest code from GitHub
echo  ===========================================
echo.

REM ===== Sync Location 1: Desktop =====
call :sync_one_dir "%DEPLOY_DIR_1%"

REM ===== Sync Location 2: D: drive (only if D: exists) =====
if exist "D:\" (
    call :sync_one_dir "%DEPLOY_DIR_2%"
) else (
    echo  [SKIP] D: drive not found - skipping %DEPLOY_DIR_2%
)

echo.
goto :eof

REM ============================================================
REM   SYNC ONE DIR - Clone or pull a single location
REM ============================================================
:sync_one_dir
set "TARGET_DIR=%~1"
echo  --- %TARGET_DIR% ---

if not exist "%TARGET_DIR%" (
    echo     Folder not found. Cloning...
    git clone -b %BRANCH% "%REPO_URL%" "%TARGET_DIR%"
    if errorlevel 1 (
        echo     [WARN] Clone failed for %TARGET_DIR% - skipping.
    ) else (
        echo     Clone complete.
    )
) else (
    if exist "%TARGET_DIR%\.git" (
        echo     Pulling latest changes...
        cd /d "%TARGET_DIR%"
        git fetch origin %BRANCH%
        if not errorlevel 1 (
            git reset --hard origin/%BRANCH%
            echo     Updated to latest.
        ) else (
            echo     [WARN] Git fetch failed - using existing files.
        )
    ) else (
        echo     Not a git repo. Removing and re-cloning...
        rmdir /s /q "%TARGET_DIR%"
        git clone -b %BRANCH% "%REPO_URL%" "%TARGET_DIR%"
        if errorlevel 1 (
            echo     [WARN] Clone failed for %TARGET_DIR% - skipping.
        ) else (
            echo     Clone complete.
        )
    )
)
echo.
goto :eof

REM ============================================================
REM   SETUP - Ensure PM2, Python venv, Node modules
REM ============================================================
:do_setup
echo  [1/3] Checking PM2...
where pm2 >nul 2>&1
if errorlevel 1 (
    echo     Installing PM2 globally...
    call npm install -g pm2
)

echo  [2/3] Setting up Python environment...
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

if not exist "%VENV_DIR%" (
    echo     Creating virtual environment...
    %PYEXE% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo  ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
)

echo     Upgrading pip...
"%PIP%" install --upgrade pip setuptools wheel --quiet

echo     Installing packages...
"%PIP%" install --prefer-binary -r "%BACKEND_DIR%\requirements.txt"
if errorlevel 1 (
    echo  ERROR: Package install failed!
    pause
    exit /b 1
)

echo  [3/3] Checking Node dependencies...
if not exist "%FRONTEND_DIR%\node_modules" (
    echo     Installing npm packages...
    pushd "%FRONTEND_DIR%"
    call npm install
    popd
)
goto :eof

REM ============================================================
REM   START - Auto: Pull + Setup + Start PM2
REM ============================================================
:do_start
cls
echo.
echo  ============================================
echo    CCPL Inventory ERP
echo  ============================================
echo.

call :do_pull
call :do_setup

echo.
echo  Starting servers with PM2...
pm2 delete ccpl-backend ccpl-frontend >nul 2>&1
cd /d "%PROJECT_DIR%"
pm2 start ecosystem.config.cjs

echo.
echo  ============================================
echo    Servers running in background
echo  ============================================
echo.
echo  Backend  : http://localhost:8000
echo  Frontend : http://localhost:8085
echo.
echo  ============================================
echo    What would you like to do?
echo  ============================================
echo.
echo    1.  Logs     (View live logs)
echo    2.  Status   (Check server status)
echo    3.  Restart  (Pull latest + restart)
echo    4.  Stop     (Stop all servers)
echo    0.  Exit     (Servers keep running)
echo.
goto :post_menu

REM ============================================================
REM   POST-START MENU
REM ============================================================
:post_menu
set /p "CHOICE=  Enter choice [0-4]: "

if "%CHOICE%"=="1" goto :do_logs_menu
if "%CHOICE%"=="2" goto :do_status_menu
if "%CHOICE%"=="3" goto :do_restart
if "%CHOICE%"=="4" goto :do_stop_menu
if "%CHOICE%"=="0" goto :exit_clean
echo  Invalid choice.
goto :post_menu

:do_logs_menu
echo.
echo  Showing live logs (Ctrl+C to return)...
echo.
pm2 logs --lines 50
goto :post_menu

:do_status_menu
echo.
pm2 status
echo.
goto :post_menu

:do_stop_menu
echo.
echo  Stopping servers...
pm2 stop ccpl-backend ccpl-frontend 2>nul
echo  Servers stopped.
echo.
goto :post_menu

REM ============================================================
REM   STOP (CLI)
REM ============================================================
:do_stop
echo.
echo  Stopping servers...
pm2 stop ccpl-backend ccpl-frontend 2>nul
if errorlevel 1 (
    echo  No servers were running.
) else (
    echo  Servers stopped.
)
echo.
goto :exit_clean

REM ============================================================
REM   RESTART (CLI + Menu)
REM ============================================================
:do_restart
echo.
echo  ============================================
echo    Restarting CCPL ERP
echo  ============================================
echo.

call :do_pull
call :do_setup

echo.
echo  Restarting servers...
pm2 delete ccpl-backend ccpl-frontend >nul 2>&1
cd /d "%PROJECT_DIR%"
pm2 start ecosystem.config.cjs

echo.
echo  Servers restarted.
echo  Backend  : http://localhost:8000
echo  Frontend : http://localhost:8085
echo.
if "%~1"=="" goto :post_menu
goto :exit_clean

REM ============================================================
REM   STATUS (CLI)
REM ============================================================
:do_status
echo.
pm2 status
echo.
goto :exit_clean

REM ============================================================
REM   LOGS (CLI)
REM ============================================================
:do_logs
echo.
echo  Showing live logs (Ctrl+C to exit)...
echo.
pm2 logs --lines 50
goto :exit_clean

REM ============================================================
:exit_clean
pause
exit /b 0
