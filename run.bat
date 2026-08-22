@echo off
setlocal
set "DIR=%~dp0"

if not exist "%DIR%.venv\Scripts\python.exe" (
    echo Virtual environment not found. Run this first:
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install -r requirements.txt
    exit /b 1
)

"%DIR%.venv\Scripts\python.exe" "%DIR%split_spritesheet.py" %*
