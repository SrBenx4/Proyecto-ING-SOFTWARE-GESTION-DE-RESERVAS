@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    where python >nul 2>nul
    if errorlevel 1 (
        echo No se encontro Python. Instale Python 3.10 o superior y vuelva a intentarlo.
        pause
        exit /b 1
    )
    set "PYTHON=python"
) else (
    set "PYTHON=py -3"
)

if not exist ".venv\Scripts\python.exe" (
    echo Preparando el entorno de la aplicacion...
    %PYTHON% -m venv .venv
    if errorlevel 1 (
        echo No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)

".venv\Scripts\python.exe" -c "import customtkinter" >nul 2>nul
if errorlevel 1 (
    echo Instalando las dependencias necesarias...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo No se pudieron instalar las dependencias. Revise su conexion a Internet.
        pause
        exit /b 1
    )
)

".venv\Scripts\python.exe" main.py
if errorlevel 1 (
    echo La aplicacion termino con un error.
    pause
    exit /b 1
)
