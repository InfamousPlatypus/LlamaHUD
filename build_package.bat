@echo off
rem Build script for creating single executable distribution

echo Building Notifs.exe...
call build_notifs.bat
if %errorlevel% neq 0 (
    echo Notifs build failed. Exiting.
    exit /b %errorlevel%
)

echo.
echo Building LlamaHUD executable with PyInstaller...
.\.venv\Scripts\pyinstaller --clean --onefile LlamaHUD.spec

if %errorlevel% neq 0 (
    echo PyInstaller build failed.
    exit /b %errorlevel%
)

echo.
echo Build complete! Executable is in dist\LlamaHUD.exe
echo.
pause
