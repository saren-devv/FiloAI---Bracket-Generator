#!/bin/bash

echo ""
echo "========================================"
echo "    FILO 0.5 - Generador de Torneos"
echo "========================================"
echo ""
echo "Iniciando aplicacion web..."
echo ""
echo "Si es la primera vez, se instalaran las dependencias..."
echo ""

# Verificar si existe el entorno virtual
if [ ! -d ".venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv .venv
fi

# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias si es necesario
echo "Instalando dependencias..."
pip install -r requirements_web.txt

# Iniciar la aplicacion
echo ""
echo "========================================"
echo "    Aplicacion iniciada exitosamente!"
echo "========================================"
echo ""
echo "Abre tu navegador y ve a:"
echo "    http://localhost:5000"
echo ""
echo "Presiona Ctrl+C para detener la aplicacion"
echo ""

python app.py 