#!/usr/bin/env python3
"""
Script de diagnóstico para FILO 0.5 - Identifica problemas comunes
"""

import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """Verificar versión de Python."""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    print(f"   Versión: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("   ⚠️  Se recomienda Python 3.7 o superior")
        return False
    else:
        print("   ✅ Versión de Python compatible")
        return True

def check_required_files():
    """Verificar archivos requeridos."""
    print("\n📁 Verificando archivos requeridos...")
    
    required_files = [
        '0.5_filo_windows.py',
        'categorias_taekwondo.json',
        'bracket_templates'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            if os.path.isdir(file):
                print(f"   ✅ {file}/ (carpeta)")
            else:
                print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - NO ENCONTRADO")
            all_exist = False
    
    return all_exist

def check_dependencies():
    """Verificar dependencias instaladas."""
    print("\n📦 Verificando dependencias...")
    
    dependencies = [
        'flask',
        'flask_cors',
        'pandas',
        'openpyxl',
        'reportlab',
        'PIL',
        'cv2',
        'numpy'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            if dep == 'PIL':
                import PIL
                print(f"   ✅ {dep}")
            elif dep == 'cv2':
                import cv2
                print(f"   ✅ {dep}")
            elif dep == 'flask_cors':
                import flask_cors
                print(f"   ✅ {dep}")
            else:
                importlib.import_module(dep)
                print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - NO INSTALADO")
            missing.append(dep)
    
    return len(missing) == 0, missing

def check_port_availability():
    """Verificar si el puerto 5000 está disponible."""
    print("\n🔌 Verificando puerto 5000...")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("   ⚠️  Puerto 5000 está en uso")
            print("   💡 Otro proceso puede estar usando el puerto")
            return False
        else:
            print("   ✅ Puerto 5000 disponible")
            return True
    except Exception as e:
        print(f"   ❌ Error verificando puerto: {e}")
        return False

def test_flask_import():
    """Probar importación de Flask."""
    print("\n🧪 Probando importación de Flask...")
    
    try:
        from flask import Flask
        app = Flask(__name__)
        print("   ✅ Flask se puede importar correctamente")
        return True
    except Exception as e:
        print(f"   ❌ Error importando Flask: {e}")
        return False

def run_quick_test():
    """Ejecutar prueba rápida del servidor."""
    print("\n🚀 Ejecutando prueba rápida del servidor...")
    
    try:
        # Importar y crear app de prueba
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/test')
        def test():
            return {'status': 'ok'}
        
        # Iniciar servidor en thread separado
        import threading
        import time
        
        def run_server():
            app.run(host='localhost', port=5001, debug=False, use_reloader=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Esperar un momento para que el servidor inicie
        time.sleep(2)
        
        # Probar conexión
        import requests
        response = requests.get('http://localhost:5001/test', timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Servidor de prueba funcionando")
            return True
        else:
            print(f"   ❌ Error en servidor de prueba: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en prueba del servidor: {e}")
        return False

def main():
    """Ejecutar diagnóstico completo."""
    print("🔍 DIAGNÓSTICO FILO 0.5")
    print("=" * 50)
    
    # Ejecutar todas las verificaciones
    checks = [
        ("Versión de Python", check_python_version),
        ("Archivos requeridos", check_required_files),
        ("Dependencias", lambda: check_dependencies()[0]),
        ("Puerto 5000", check_port_availability),
        ("Importación Flask", test_flask_import),
        ("Prueba servidor", run_quick_test)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Error en {name}: {e}")
            results.append((name, False))
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 50)
    
    passed = 0
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} verificaciones pasaron")
    
    if passed == len(results):
        print("\n🎉 ¡Todo está funcionando correctamente!")
        print("💡 Puedes ejecutar: python server.py")
    else:
        print("\n⚠️  Se encontraron problemas:")
        print("💡 Revisa los errores arriba y corrígelos")
        
        # Verificar dependencias faltantes
        _, missing_deps = check_dependencies()
        if missing_deps:
            print(f"\n📦 Para instalar dependencias faltantes:")
            print(f"   pip install {' '.join(missing_deps)}")
            print("   O ejecuta: pip install -r requirements_web.txt")

if __name__ == "__main__":
    main() 