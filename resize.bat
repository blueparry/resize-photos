@echo off
REM Cross-platform launcher for Photo Resizer (Windows)
REM Usage:
REM   resize.bat          - opens GUI
REM   resize.bat --cli    - runs CLI mode (pass args after --cli)

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%.venv

if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
    "%VENV_DIR%\Scripts\pip" install --quiet Pillow
)

if "%1"=="--cli" (
    shift
    "%VENV_DIR%\Scripts\python" "%SCRIPT_DIR%resize.py" %*
) else (
    "%VENV_DIR%\Scripts\python" "%SCRIPT_DIR%resize_gui.py" %*
)
