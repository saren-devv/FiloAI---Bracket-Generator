#!/usr/bin/env python3
"""
Test con los datos exactos que está enviando el frontend
"""
import requests
import json

def test_exact_frontend_data():
    """Prueba con los datos exactos del frontend"""
    
    # Datos exactos del frontend (simplificados para test)
    exact_data = {
        "brackets": [
            {
                "category": "Noveles INFANTIL B MASCULINO -30",
                "participants": [
                    {
                        "name": "JOAQUÍN DANIEL BOBADILLA DÍAZ",
                        "academy": "DGA"
                    },
                    {
                        "name": "HEVER OMAR CARLOS FERNANDEZ",
                        "academy": "DGA"
                    }
                ],
                "type": "single_elimination"
            }
        ]
    }
    
    print("🧪 Probando con datos exactos del frontend...")
    print(f"📊 Datos: {json.dumps(exact_data, indent=2)}")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/generate-pdf',
            json=exact_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PDF generado exitosamente")
            with open('test_exact_output.pdf', 'wb') as f:
                f.write(response.content)
            print("💾 PDF guardado como 'test_exact_output.pdf'")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Respuesta: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("⏱️ Timeout - El servidor tardó más de 30 segundos")
    except Exception as e:
        print(f"❌ Error en la petición: {e}")

if __name__ == '__main__':
    test_exact_frontend_data()