@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    where py >nul 2>nul
    if not errorlevel 1 (
        py -3 -m venv .venv
    ) else (
        python -m venv .venv
    )
)

set "PY=.venv\Scripts\python.exe"

"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r requirements.txt -r requirements-build.txt
if errorlevel 1 goto :error

"%PY%" -m PyInstaller --noconfirm TextureSplitter.spec
if errorlevel 1 goto :error

echo.
echo Done. Executable is in the dist\ folder:
echo   dist\TextureSplitter.exe      (GUI)
pause
exit /b 0

:error
echo.
echo Build failed. See the errors above.
pause
exit /b 1
