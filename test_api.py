#!/usr/bin/env python3
"""
Script para probar los endpoints de la API
"""
import requests
import json

def test_api():
    base_url = 'http://localhost:5000'
    
    print("🧪 Probando endpoints de la API...")
    
    # Probar endpoint de status
    try:
        r = requests.get(f'{base_url}/status')
        print(f"✅ /status: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"❌ /status: Error - {e}")
    
    # Probar endpoint de process-file sin archivo
    try:
        r = requests.post(f'{base_url}/api/process-file')
        print(f"✅ /api/process-file (sin archivo): {r.status_code} - {r.text[:100]}")
    except Exception as e:
        print(f"❌ /api/process-file: Error - {e}")
    
    # Listar todas las rutas disponibles
    print("\n📋 Rutas disponibles:")
    try:
        # Importar la app para ver las rutas
        import sys
        sys.path.append('.')
        import app
        for rule in app.app.url_map.iter_rules():
            print(f"  {rule.rule} - {list(rule.methods)}")
    except Exception as e:
        print(f"❌ Error listando rutas: {e}")

if __name__ == '__main__':
    test_api()