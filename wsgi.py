#!/usr/bin/env python3
"""
WSGI entry point para FILO 0.5
Compatible con Render, Railway, Heroku y otros servidores WSGI
"""

import os
from app import app

if __name__ == "__main__":
    # Configuración específica para Render
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🚀 Iniciando FILO 0.5 via WSGI...")
    print(f"🌐 Puerto: {port}")
    print(f"🔧 Debug: {app.config['DEBUG']}")
    
    # En Render, usar configuración específica
    app.run(
        host='0.0.0.0',  # Siempre 0.0.0.0 en Render
        port=port,
        debug=False,  # Siempre False en producción
        threaded=True,  # Habilitar threading
        processes=1  # Un solo proceso
    )
