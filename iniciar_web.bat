@echo off
echo.
echo ========================================
echo    FILO 0.5 - Generador de Torneos
echo ========================================
echo.
echo Iniciando aplicacion web...
echo.
echo Si es la primera vez, se instalaran las dependencias...
echo.

REM Verificar si existe el entorno virtual
if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
)

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Instalar dependencias si es necesario
echo Instalando dependencias...
pip install -r requirements_web.txt

REM Iniciar la aplicacion
echo.
echo ========================================
echo    Aplicacion iniciada exitosamente!
echo ========================================
echo.
echo Abre tu navegador y ve a:
echo    http://localhost:5000
echo.
echo Presiona Ctrl+C para detener la aplicacion
echo.

python app.py

pause 