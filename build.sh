#!/bin/bash
echo "🚀 Iniciando build de FILO 0.5..."

# Mostrar información del sistema
echo "🐍 Python version:"
python --version
echo "📁 Current directory:"
pwd
echo "📋 Directory contents:"
ls -la

# Actualizar pip
echo "📦 Actualizando pip..."
python -m pip install --upgrade pip

# Instalar dependencias base primero
echo "🔧 Instalando dependencias base..."
pip install --upgrade setuptools wheel

# Instalar Flask y Flask-CORS primero
echo "🔧 Instalando Flask y Flask-CORS..."
pip install Flask Flask-CORS

# Verificar instalación
echo "✅ Verificando instalación..."
python -c "import flask; print('Flask version:', flask.__version__)"
python -c "import flask_cors; print('Flask-CORS version:', flask_cors.__version__)"

# Instalar numpy y pandas con flags específicos
echo "📊 Instalando numpy y pandas..."
pip install --only-binary=all numpy
pip install --only-binary=all pandas

# Instalar resto de dependencias
echo "📚 Instalando resto de dependencias..."
if pip install -r requirements_web.txt; then
    echo "✅ Dependencias instaladas exitosamente desde requirements_web.txt"
else
    echo "⚠️ Fallback a requirements_binary.txt..."
    pip install -r requirements_binary.txt
fi

echo "🎉 Build completado exitosamente!" 