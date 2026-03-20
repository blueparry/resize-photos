@echo off
REM Redimensionar Fotos - Launcher para Windows
REM Clique duas vezes para abrir a interface grafica.

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%.venv

REM Verificar se o Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================
    echo   Python nao encontrado!
    echo.
    echo   Por favor, instale o Python:
    echo   https://www.python.org/downloads/
    echo.
    echo   IMPORTANTE: Marque a opcao
    echo   "Add Python to PATH" durante a instalacao.
    echo ============================================
    echo.
    pause
    exit /b 1
)

REM Criar ambiente virtual se nao existir
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo.
    echo A preparar o programa pela primeira vez...
    echo Isto pode demorar um momento.
    echo.
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo.
        echo Erro ao criar ambiente virtual.
        pause
        exit /b 1
    )
    "%VENV_DIR%\Scripts\pip" install --quiet Pillow
    if errorlevel 1 (
        echo.
        echo Erro ao instalar dependencias.
        pause
        exit /b 1
    )
    echo Pronto!
    echo.
)

REM Abrir a interface grafica
if "%~1"=="--cli" (
    shift
    "%VENV_DIR%\Scripts\python" "%SCRIPT_DIR%resize.py" %*
) else (
    start "" "%VENV_DIR%\Scripts\pythonw" "%SCRIPT_DIR%resize_gui.py" %*
)

if errorlevel 1 (
    echo.
    echo Algo correu mal ao abrir o programa.
    pause
)
