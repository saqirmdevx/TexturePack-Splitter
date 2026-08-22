@echo off
cd /d "%~dp0"

set "PYTHON_EXE="

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    where py >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_EXE=py"
    ) else (
        where python >nul 2>nul
        if not errorlevel 1 set "PYTHON_EXE=python"
    )
)

if not defined PYTHON_EXE (
    echo.
    echo Python was not found on this computer.
    echo Install it from https://www.python.org/downloads/
    echo During setup, make sure to check "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)

"%PYTHON_EXE%" app.py
pause
