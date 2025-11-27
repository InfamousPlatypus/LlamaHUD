@echo off
rem Build Notifs C# program
call build_notifs.bat
if %errorlevel% neq 0 (
    echo Notifs build failed. Exiting.
    exit /b %errorlevel%
)

rem Launch HUD (Python) using .venv
if exist .\.venv\Scripts\python.exe (
    .\.venv\Scripts\python.exe HUD.py
) else (
    echo Virtual environment not found. Please run setup first.
    exit /b 1
)

rem After HUD window closed, exit
exit /b 0
