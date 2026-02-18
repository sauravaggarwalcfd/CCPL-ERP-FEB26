@echo off
title CCPL ERP - Stop

echo.
echo  Stopping CCPL ERP servers...
echo.

REM Kill the titled CMD windows
taskkill /FI "WINDOWTITLE eq CCPL-Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq CCPL-Frontend*" /T /F >nul 2>&1

REM Also kill by process on the ports as a fallback
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8085 " ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo  Backend  (port 8000) - STOPPED
echo  Frontend (port 8085) - STOPPED
echo.
echo  All CCPL ERP servers have been stopped.
echo.
timeout /t 2 /nobreak >nul
