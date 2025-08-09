# 🚀 Guía de Deploy - FILO 0.5

## 📋 Estado del Proyecto

✅ **FILO 0.5 está completamente listo para deploy**

### 🔧 Funcionalidades Implementadas
- ✅ Interfaz web completa para gestión de torneos
- ✅ Carga y procesamiento de archivos Excel
- ✅ Generación automática de brackets
- ✅ Editor visual de llaves
- ✅ Gestión de categorías y participantes
- ✅ Generación de PDFs con estilo Mexxus Arena
- ✅ API REST completa
- ✅ Configuración de producción

## 🌐 Plataformas de Deploy Soportadas

### 1. **Render** (Recomendado)
- **Archivo de configuración:** `render.yaml`
- **URL:** https://render.com
- **Ventajas:** Gratuito, fácil de usar, auto-deploy

### 2. **Railway**
- **Archivo de configuración:** `railway.json`
- **URL:** https://railway.app
- **Ventajas:** Rápido, buena integración con Git

### 3. **Heroku**
- **Archivo de configuración:** `Procfile`
- **URL:** https://heroku.com
- **Ventajas:** Estable, buena documentación

## 📁 Archivos de Configuración

| Archivo | Descripción | Plataforma |
|---------|-------------|------------|
| `render.yaml` | Configuración completa para Render | Render |
| `railway.json` | Configuración para Railway | Railway |
| `Procfile` | Configuración para Heroku | Heroku |
| `requirements_web.txt` | Dependencias de Python | Todas |
| `config.py` | Configuración de la aplicación | Todas |
| `build.sh` | Script de build | Todas |

## 🚀 Pasos para el Deploy

### Paso 1: Preparar el Repositorio
```bash
# Ejecutar script de preparación (Windows)
.\deploy.ps1

# O en Linux/Mac
./deploy.sh
```

### Paso 2: Subir Cambios a Git
```bash
git add .
git commit -m "Deploy v0.5 - Ready for production"
git push origin main
```

### Paso 3: Deploy en la Plataforma Elegida

#### **Render (Recomendado)**
1. Ir a https://render.com
2. Conectar repositorio de GitHub
3. Seleccionar "New Web Service"
4. El archivo `render.yaml` se detectará automáticamente
5. Hacer click en "Create Web Service"

#### **Railway**
1. Ir a https://railway.app
2. Conectar repositorio de GitHub
3. Seleccionar el repositorio
4. Railway detectará automáticamente la configuración
5. Hacer deploy

#### **Heroku**
1. Ir a https://heroku.com
2. Crear nueva app
3. Conectar repositorio de GitHub
4. Habilitar auto-deploy
5. Hacer deploy manual inicial

## ⚙️ Variables de Entorno

### **Obligatorias**
- `FLASK_ENV`: `production`
- `PYTHON_VERSION`: `3.11.7`

### **Opcionales**
- `SECRET_KEY`: Clave secreta (se genera automáticamente en Render)
- `PORT`: Puerto del servidor (se establece automáticamente)

## 🔍 Verificación del Deploy

### 1. **Health Check**
- Endpoint: `/status`
- Debe retornar: `{"status": "ok", "timestamp": "..."}`

### 2. **Funcionalidades Principales**
- ✅ Página de inicio: `/`
- ✅ Editor: `/editor`
- ✅ Generador: `/generator`
- ✅ API de procesamiento: `/api/process-file`
- ✅ API de generación PDF: `/api/generate-pdf`

### 3. **Logs del Servidor**
- Verificar que no haya errores de importación
- Verificar que las carpetas se creen correctamente
- Verificar que el servidor esté escuchando en el puerto correcto

## 🐛 Solución de Problemas Comunes

### **Error: "No module named 'flask'**
- **Solución:** Verificar que `requirements_web.txt` esté en el repositorio
- **Verificar:** El archivo debe contener todas las dependencias

### **Error: "Port already in use"**
- **Solución:** La variable `PORT` se establece automáticamente en producción
- **Verificar:** No hay puertos hardcodeados en `app.py`

### **Error: "Upload folder not found"**
- **Solución:** Las carpetas se crean automáticamente
- **Verificar:** El script de build debe ejecutarse correctamente

### **Error: "Categories not defined"**
- **Solución:** ✅ **CORREGIDO** - Variable `categories` ahora está definida globalmente

## 📊 Monitoreo en Producción

### **Métricas a Monitorear**
- Tiempo de respuesta de la API
- Uso de memoria
- Errores 500
- Tiempo de procesamiento de archivos Excel

### **Logs Importantes**
- Procesamiento de archivos
- Generación de PDFs
- Errores de la aplicación
- Accesos a endpoints críticos

## 🔄 Actualizaciones

### **Para futuras versiones:**
1. Actualizar `VERSION.txt`
2. Hacer commit de cambios
3. Push a la rama principal
4. La plataforma hará auto-deploy

## 📞 Soporte

### **En caso de problemas:**
1. Revisar logs de la plataforma
2. Verificar variables de entorno
3. Probar endpoints de health check
4. Verificar que todas las dependencias estén instaladas

---

## 🎉 ¡FILO 0.5 está listo para conquistar el mundo del Taekwondo!

**Última actualización:** $(Get-Date)
**Versión:** 0.5
**Estado:** ✅ Ready for Production
