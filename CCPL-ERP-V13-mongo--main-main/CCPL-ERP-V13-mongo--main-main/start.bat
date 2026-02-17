@echo off
setlocal enabledelayedexpansion

echo ================================
echo Inventory ERP - Quick Start
echo ================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %errorlevel% equ 0 (
    echo Docker found
    echo.
    echo Starting with Docker Compose...
    echo.
    
    docker-compose up -d
    
    echo.
    echo ================================
    echo Services Started!
    echo ================================
    echo.
    echo MongoDB:     mongodb://localhost:27017
    echo Backend API: http://localhost:8000
    echo Frontend:    http://localhost:5173
    echo.
    echo API Docs:    http://localhost:8000/docs
    echo.
    echo View logs:   docker-compose logs -f
    echo Stop:        docker-compose down
    echo.
) else (
    echo Docker not found. Using manual setup...
    echo.
    
    REM Backend setup
    echo Ensuring MongoDB is running on localhost:27017
    echo.
    
    echo Setting up Backend...
    cd backend
    
    if not exist "venv" (
        echo Creating Python virtual environment...
        python -m venv venv
    )
    
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    
    echo Installing backend dependencies...
    pip install -r requirements.txt
    
    echo Starting backend server...
    start "" python -m uvicorn app.main:app --reload --port 8000
    
    cd ..\frontend
    
    echo.
    echo Setting up Frontend...
    
    if not exist "node_modules" (
        echo Installing frontend dependencies...
        call npm install
    )
    
    echo Starting frontend server...
    start "" npm run dev
    
    echo.
    echo ================================
    echo Services Started!
    echo ================================
    echo.
    echo Backend API: http://localhost:8000
    echo Frontend:    http://localhost:5173
    echo API Docs:    http://localhost:8000/docs
    echo.
    echo Services are running in separate windows
    echo.
)

pause
