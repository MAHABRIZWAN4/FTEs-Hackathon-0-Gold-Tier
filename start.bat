@echo off
REM Silver Tier AI Employee - Quick Start Script
REM This script helps you start your AI Employee system easily

echo.
echo ========================================================
echo    SILVER TIER AI EMPLOYEE - QUICK START
echo ========================================================
echo.

:menu
echo Choose an option:
echo.
echo [1] Test Colorful UI (Recommended First!)
echo [2] Start Gmail Watcher
echo [3] Start Vault Watcher
echo [4] Start Task Planner (Manual)
echo [5] Start Full System (Scheduler - Once)
echo [6] Start Full System (Scheduler - Daemon)
echo [7] View Logs (Real-time)
echo [8] Check System Status
echo [9] Exit
echo.
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto test_ui
if "%choice%"=="2" goto gmail_watcher
if "%choice%"=="3" goto vault_watcher
if "%choice%"=="4" goto task_planner
if "%choice%"=="5" goto scheduler_once
if "%choice%"=="6" goto scheduler_daemon
if "%choice%"=="7" goto view_logs
if "%choice%"=="8" goto check_status
if "%choice%"=="9" goto end

echo Invalid choice! Please try again.
echo.
goto menu

:test_ui
echo.
echo Starting Colorful UI Test...
echo.
python test_ui.py
echo.
pause
goto menu

:gmail_watcher
echo.
echo Starting Gmail Watcher...
echo Press Ctrl+C to stop
echo.
python scripts/watch_gmail.py
echo.
pause
goto menu

:vault_watcher
echo.
echo Starting Vault Watcher...
echo Press Ctrl+C to stop
echo.
python scripts/watch_inbox.py
echo.
pause
goto menu

:task_planner
echo.
echo Running Task Planner...
echo.
python scripts/task_planner.py
echo.
pause
goto menu

:scheduler_once
echo.
echo Running Scheduler (Single Execution)...
echo.
python scripts/run_ai_employee.py --once
echo.
pause
goto menu

:scheduler_daemon
echo.
echo Starting Scheduler (Daemon Mode)...
echo Press Ctrl+C to stop
echo.
python scripts/run_ai_employee.py
echo.
pause
goto menu

:view_logs
echo.
echo Viewing logs (Press Ctrl+C to stop)...
echo.
powershell -Command "Get-Content logs/actions.log -Wait -Tail 50"
echo.
pause
goto menu

:check_status
echo.
echo ========================================================
echo    SYSTEM STATUS CHECK
echo ========================================================
echo.
echo Checking Python...
python --version
echo.
echo Checking Rich library...
python -c "import rich; print('Rich library: OK')" 2>nul || echo Rich library: NOT INSTALLED
echo.
echo Checking .env file...
if exist .env (
    echo .env file: EXISTS
) else (
    echo .env file: NOT FOUND - Please create it!
)
echo.
echo Checking folders...
if exist AI_Employee_Vault\Inbox (
    echo Inbox folder: EXISTS
) else (
    echo Inbox folder: NOT FOUND
)
echo.
if exist logs (
    echo Logs folder: EXISTS
) else (
    echo Logs folder: NOT FOUND
)
echo.
echo Checking scripts...
if exist scripts\watch_gmail.py (
    echo Gmail Watcher: EXISTS
) else (
    echo Gmail Watcher: NOT FOUND
)
echo.
if exist scripts\watch_inbox.py (
    echo Vault Watcher: EXISTS
) else (
    echo Vault Watcher: NOT FOUND
)
echo.
echo ========================================================
echo.
pause
goto menu

:end
echo.
echo Thank you for using Silver Tier AI Employee!
echo.
exit
