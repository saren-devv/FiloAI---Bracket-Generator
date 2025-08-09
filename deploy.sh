#!/bin/bash

echo "🚀 Preparando FILO 0.5 para deploy..."

# Verificar que estamos en la rama correcta
echo "📋 Verificando rama actual..."
current_branch=$(git branch --show-current)
echo "📍 Rama actual: $current_branch"

# Verificar estado del repositorio
echo "🔍 Verificando estado del repositorio..."
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  Hay cambios sin commitear:"
    git status --porcelain
    echo ""
    read -p "¿Deseas continuar con el deploy? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deploy cancelado"
        exit 1
    fi
fi

# Verificar que no haya archivos de prueba
echo "🧹 Limpiando archivos de prueba..."
if [ -f "test_output.pdf" ]; then
    rm test_output.pdf
    echo "🗑️  Eliminado test_output.pdf"
fi

if [ -f "test_exact_output.pdf" ]; then
    rm test_exact_output.pdf
    echo "🗑️  Eliminado test_exact_output.pdf"
fi

# Verificar que las carpetas necesarias existan
echo "📁 Verificando estructura de carpetas..."
mkdir -p uploads
mkdir -p results
mkdir -p static
mkdir -p templates
mkdir -p bracket_templates
mkdir -p fonts

echo "✅ Carpetas verificadas"

# Verificar archivos críticos
echo "🔍 Verificando archivos críticos..."
critical_files=("app.py" "filo_0_5.py" "config.py" "requirements_web.txt" "templates/editor.html")
for file in "${critical_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Archivo crítico faltante: $file"
        exit 1
    fi
done

echo "✅ Archivos críticos verificados"

# Verificar que no haya errores de sintaxis en Python
echo "🐍 Verificando sintaxis de Python..."
python -m py_compile app.py
python -m py_compile config.py
python -m py_compile filo_0_5.py

if [ $? -eq 0 ]; then
    echo "✅ Sintaxis de Python verificada"
else
    echo "❌ Error de sintaxis en archivos Python"
    exit 1
fi

# Crear archivo de versión
echo "📝 Creando archivo de versión..."
version=$(date +"%Y.%m.%d-%H%M")
echo "FILO 0.5 - Versión: $version" > VERSION.txt
echo "Fecha de build: $(date)" >> VERSION.txt
echo "Git commit: $(git rev-parse --short HEAD)" >> VERSION.txt

echo "✅ Archivo de versión creado: VERSION.txt"

# Verificar configuración de producción
echo "⚙️  Verificando configuración de producción..."
if grep -q "debug.*True" app.py; then
    echo "⚠️  Advertencia: Debug puede estar habilitado en producción"
fi

echo ""
echo "🎉 FILO 0.5 está listo para deploy!"
echo "📋 Pasos para el deploy:"
echo "   1. Subir cambios a Git: git add . && git commit -m 'Deploy v$version'"
echo "   2. Hacer push: git push origin $current_branch"
echo "   3. En Render/Railway/Heroku, hacer deploy desde esta rama"
echo ""
echo "🔗 URLs de deploy:"
echo "   - Render: https://render.com (conectar repositorio)"
echo "   - Railway: https://railway.app (conectar repositorio)"
echo "   - Heroku: https://heroku.com (conectar repositorio)"
echo ""
echo "📁 Archivos de configuración listos:"
echo "   ✅ render.yaml"
echo "   ✅ railway.json"
echo "   ✅ Procfile"
echo "   ✅ requirements_web.txt"
echo "   ✅ config.py"
