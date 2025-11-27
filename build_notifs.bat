@echo off
rem Build Notifs C# program using dotnet
dotnet build Notifs.csproj -c Release
if %errorlevel% neq 0 (
    echo Build failed.
    exit /b %errorlevel%
)
rem Copy the built executable to the current directory
copy /Y "bin\Release\net6.0-windows\Notifs.exe" .
if %errorlevel% neq 0 (
    echo Copy failed.
    exit /b %errorlevel%
)
echo Build succeeded.
