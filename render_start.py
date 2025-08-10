#!/usr/bin/env python3
"""
Script de inicio específico para Render
Asegura que la aplicación se vincule correctamente y sea detectable
"""

import os
from app import app

if __name__ == '__main__':
    # Obtener puerto de Render
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🚀 Iniciando FILO 0.5 en Render...")
    print(f"📁 Carpeta de uploads: {app.config['UPLOAD_FOLDER']}")
    print(f"📁 Carpeta de resultados: {app.config['RESULTS_FOLDER']}")
    print(f"🌐 Puerto: {port}")
    print(f"🔧 Debug: {app.config['DEBUG']}")
    
    # En Render, siempre usar 0.0.0.0 para ser accesible externamente
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Siempre False en producción
    )
