# Script simple para verificar deploy de FILO 0.5
Write-Host "🚀 Verificando FILO 0.5 para deploy..." -ForegroundColor Green

# Verificar archivos críticos
Write-Host "`n🔍 Verificando archivos críticos..." -ForegroundColor Yellow
$critical_files = @("app.py", "filo_0_5.py", "config.py", "requirements_web.txt", "templates/editor.html")
foreach ($file in $critical_files) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file - FALTANTE" -ForegroundColor Red
    }
}

# Verificar archivos de configuración
Write-Host "`n⚙️  Verificando archivos de configuración..." -ForegroundColor Yellow
$config_files = @("render.yaml", "railway.json", "Procfile", "build.sh")
foreach ($file in $config_files) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file - FALTANTE" -ForegroundColor Red
    }
}

# Verificar sintaxis de Python
Write-Host "`n🐍 Verificando sintaxis de Python..." -ForegroundColor Yellow
try {
    python -m py_compile app.py
    Write-Host "✅ app.py - Sintaxis correcta" -ForegroundColor Green
} catch {
    Write-Host "❌ app.py - Error de sintaxis" -ForegroundColor Red
}

try {
    python -m py_compile config.py
    Write-Host "✅ config.py - Sintaxis correcta" -ForegroundColor Green
} catch {
    Write-Host "❌ config.py - Error de sintaxis" -ForegroundColor Red
}

# Verificar carpetas
Write-Host "`n📁 Verificando estructura de carpetas..." -ForegroundColor Yellow
$folders = @("uploads", "results", "static", "templates", "bracket_templates", "fonts")
foreach ($folder in $folders) {
    if (Test-Path $folder) {
        Write-Host "✅ $folder" -ForegroundColor Green
    } else {
        Write-Host "❌ $folder - FALTANTE" -ForegroundColor Red
    }
}

Write-Host "`n🎉 Verificación completada!" -ForegroundColor Green
Write-Host "`n📋 Para hacer deploy:" -ForegroundColor Cyan
Write-Host "   1. git add ." -ForegroundColor White
Write-Host "   2. git commit -m 'Deploy v0.5 - Ready for production'" -ForegroundColor White
Write-Host "   3. git push origin main" -ForegroundColor White
Write-Host "   4. Conectar repositorio en Render/Railway/Heroku" -ForegroundColor White
