@echo off
setlocal
title Mision Numerica v4.0 // Nave Aurora
cd /d "%~dp0"
set "PYTHONDONTWRITEBYTECODE=1"

set "PY_CMD="
if exist ".venv\Scripts\python.exe" set "PY_CMD=.venv\Scripts\python.exe"
if not defined PY_CMD (
    where python >nul 2>nul && set "PY_CMD=python"
)
if not defined PY_CMD (
    where py >nul 2>nul && set "PY_CMD=py -3"
)

if not defined PY_CMD (
    echo [ERROR] No se encontro Python 3 en el sistema.
    echo Instala Python 3 e instala dependencias con: pip install -r requerimientos.txt
    pause
    exit /b 1
)

%PY_CMD% -B "MisionNumerica_V2\nave.py"
if errorlevel 1 (
    echo.
    echo [AVISO] Si falta Pillow o Matplotlib, ejecuta: pip install -r requerimientos.txt
    pause
    exit /b 1
)
