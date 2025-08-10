#!/usr/bin/env python3
"""
Configuración específica para Render
Asegura que la aplicación se vincule correctamente en el entorno de Render
"""

import os

# Configuración específica para Render
RENDER_CONFIG = {
    'HOST': '0.0.0.0',  # Siempre 0.0.0.0 en Render
    'PORT': int(os.environ.get('PORT', 5000)),
    'DEBUG': False,  # Siempre False en producción
    'THREADED': True,  # Habilitar threading para mejor rendimiento
    'PROCESSES': 1,  # Un solo proceso para evitar conflictos
}

print(f"🔧 Configuración Render cargada:")
print(f"   HOST: {RENDER_CONFIG['HOST']}")
print(f"   PORT: {RENDER_CONFIG['PORT']}")
print(f"   DEBUG: {RENDER_CONFIG['DEBUG']}")
print(f"   THREADED: {RENDER_CONFIG['THREADED']}")
print(f"   PROCESSES: {RENDER_CONFIG['PROCESSES']}")
