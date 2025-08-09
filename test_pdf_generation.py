#!/usr/bin/env python3
"""
Script para probar la generación de PDF directamente
"""
import requests
import json

def test_pdf_generation():
    """Prueba la generación de PDF con datos de ejemplo"""
    
    # Datos de ejemplo que debería enviar el frontend
    test_data = {
        "brackets": [
            {
                "id": "bracket_test_1",
                "category": "Festival Infantil A Masculino -27",
                "participants": [
                    {
                        "name": "Juan Pérez",
                        "academy": "UAEM"
                    },
                    {
                        "name": "Carlos López",
                        "academy": "UAZ"
                    }
                ]
            },
            {
                "id": "bracket_test_2", 
                "category": "Festival Infantil A Femenino -30",
                "participants": [
                    {
                        "name": "María González",
                        "academy": "UANL"
                    },
                    {
                        "name": "Ana Martínez", 
                        "academy": "UDG"
                    }
                ]
            }
        ]
    }
    
    print("🧪 Probando generación de PDF...")
    print(f"📊 Datos a enviar: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/generate-pdf',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📡 Respuesta del servidor: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PDF generado exitosamente")
            # Guardar el PDF
            with open('test_output.pdf', 'wb') as f:
                f.write(response.content)
            print("💾 PDF guardado como 'test_output.pdf'")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")

if __name__ == '__main__':
    test_pdf_generation()