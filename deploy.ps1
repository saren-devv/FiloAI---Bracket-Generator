# Script de deploy para FILO 0.5 en PowerShell
Write-Host "🚀 Preparando FILO 0.5 para deploy..." -ForegroundColor Green

# Verificar que estamos en la rama correcta
Write-Host "📋 Verificando rama actual..." -ForegroundColor Yellow
$current_branch = git branch --show-current
Write-Host "📍 Rama actual: $current_branch" -ForegroundColor Cyan

# Verificar estado del repositorio
Write-Host "🔍 Verificando estado del repositorio..." -ForegroundColor Yellow
$status = git status --porcelain
if ($status) {
    Write-Host "⚠️  Hay cambios sin commitear:" -ForegroundColor Yellow
    Write-Host $status -ForegroundColor Red
    Write-Host ""
    $response = Read-Host "¿Deseas continuar con el deploy? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "❌ Deploy cancelado" -ForegroundColor Red
        exit 1
    }
}

# Verificar que no haya archivos de prueba
Write-Host "🧹 Limpiando archivos de prueba..." -ForegroundColor Yellow
if (Test-Path "test_output.pdf") {
    Remove-Item "test_output.pdf"
    Write-Host "🗑️  Eliminado test_output.pdf" -ForegroundColor Green
}

if (Test-Path "test_exact_output.pdf") {
    Remove-Item "test_exact_output.pdf"
    Write-Host "🗑️  Eliminado test_exact_output.pdf" -ForegroundColor Green
}

# Verificar que las carpetas necesarias existan
Write-Host "📁 Verificando estructura de carpetas..." -ForegroundColor Yellow
$folders = @("uploads", "results", "static", "templates", "bracket_templates", "fonts")
foreach ($folder in $folders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force
        Write-Host "📁 Creada carpeta: $folder" -ForegroundColor Green
    }
}

Write-Host "✅ Carpetas verificadas" -ForegroundColor Green

# Verificar archivos críticos
Write-Host "🔍 Verificando archivos críticos..." -ForegroundColor Yellow
$critical_files = @("app.py", "filo_0_5.py", "config.py", "requirements_web.txt", "templates/editor.html")
foreach ($file in $critical_files) {
    if (!(Test-Path $file)) {
        Write-Host "❌ Archivo crítico faltante: $file" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Archivos críticos verificados" -ForegroundColor Green

# Verificar que no haya errores de sintaxis en Python
Write-Host "🐍 Verificando sintaxis de Python..." -ForegroundColor Yellow
try {
    python -m py_compile app.py
    python -m py_compile config.py
    python -m py_compile filo_0_5.py
    Write-Host "✅ Sintaxis de Python verificada" -ForegroundColor Green
} catch {
    Write-Host "❌ Error de sintaxis en archivos Python" -ForegroundColor Red
    exit 1
}

# Crear archivo de versión
Write-Host "📝 Creando archivo de versión..." -ForegroundColor Yellow
$version = Get-Date -Format "yyyy.MM.dd-HHmm"
$gitCommit = git rev-parse --short HEAD
$versionContent = "FILO 0.5 - Versión: $version`nFecha de build: $(Get-Date)`nGit commit: $gitCommit"
$versionContent | Out-File -FilePath "VERSION.txt" -Encoding UTF8

Write-Host "✅ Archivo de versión creado: VERSION.txt" -ForegroundColor Green

# Verificar configuración de producción
Write-Host "⚙️  Verificando configuración de producción..." -ForegroundColor Yellow
$debugCheck = Select-String -Path "app.py" -Pattern "debug.*True" -Quiet
if ($debugCheck) {
    Write-Host "⚠️  Advertencia: Debug puede estar habilitado en producción" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 FILO 0.5 está listo para deploy!" -ForegroundColor Green
Write-Host "📋 Pasos para el deploy:" -ForegroundColor Cyan
Write-Host "   1. Subir cambios a Git: git add . && git commit -m 'Deploy v$version'" -ForegroundColor White
Write-Host "   2. Hacer push: git push origin $current_branch" -ForegroundColor White
Write-Host "   3. En Render/Railway/Heroku, hacer deploy desde esta rama" -ForegroundColor White
Write-Host ""
Write-Host "🔗 URLs de deploy:" -ForegroundColor Cyan
Write-Host "   - Render: https://render.com (conectar repositorio)" -ForegroundColor White
Write-Host "   - Railway: https://railway.app (conectar repositorio)" -ForegroundColor White
Write-Host "   - Heroku: https://heroku.com (conectar repositorio)" -ForegroundColor White
Write-Host ""
Write-Host "📁 Archivos de configuración listos:" -ForegroundColor Cyan
Write-Host "   ✅ render.yaml" -ForegroundColor Green
Write-Host "   ✅ railway.json" -ForegroundColor Green
Write-Host "   ✅ Procfile" -ForegroundColor Green
Write-Host "   ✅ requirements_web.txt" -ForegroundColor Green
Write-Host "   ✅ config.py" -ForegroundColor Green
