@echo off
REM Cross-platform wrapper for resize.py (Windows)
REM Usage: resize.bat [--max-size 1024] [--quality 85] [--no-backup]

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%.venv

if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
    "%VENV_DIR%\Scripts\pip" install --quiet Pillow
)

"%VENV_DIR%\Scripts\python" "%SCRIPT_DIR%resize.py" %*
