#!/bin/bash
echo "🚀 Iniciando build de FILO 0.5..."

# Actualizar pip
echo "📦 Actualizando pip..."
python -m pip install --upgrade pip

# Instalar Flask y Flask-CORS primero
echo "🔧 Instalando Flask y Flask-CORS..."
pip install Flask Flask-CORS

# Verificar instalación
echo "✅ Verificando instalación..."
python -c "import flask; print('Flask version:', flask.__version__)"
python -c "import flask_cors; print('Flask-CORS version:', flask_cors.__version__)"

# Instalar resto de dependencias
echo "📚 Instalando resto de dependencias..."
pip install -r requirements_web.txt

echo "🎉 Build completado exitosamente!" 