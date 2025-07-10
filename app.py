#!/usr/bin/env python3
"""
FILO 0.5 Web App - Interfaz web para gestión de torneos de Taekwondo
Autor: AI Assistant
Fecha: 2024
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import tempfile
import shutil
from pathlib import Path
import zipfile
from datetime import datetime
import traceback

# Importar la lógica existente
from filo_0_5 import AgrupadorMultiple, generar_brackets_desde_excel, generar_resumen_torneo

app = Flask(__name__)
CORS(app)

# Configuración
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

# Crear carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No se seleccionaron archivos'}), 400
        
        files = request.files.getlist('files[]')
        if not files or files[0].filename == '':
            return jsonify({'error': 'No se seleccionaron archivos'}), 400
        
        # Crear carpeta temporal para este procesamiento
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'procesamiento_{timestamp}')
        os.makedirs(temp_folder, exist_ok=True)
        
        # Guardar archivos subidos
        uploaded_files = []
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = file.filename
                filepath = os.path.join(temp_folder, filename)
                file.save(filepath)
                uploaded_files.append(filepath)
        
        if not uploaded_files:
            return jsonify({'error': 'No se pudieron guardar archivos válidos'}), 400
        
        # Procesar archivos usando la lógica existente
        carpeta_salida = os.path.join(app.config['RESULTS_FOLDER'], f'torneo_{timestamp}')
        os.makedirs(carpeta_salida, exist_ok=True)
        
        # Procesar archivos usando la lógica existente
        agrupador = AgrupadorMultiple()
        
        # Procesar archivos
        df = agrupador.procesar_multiples_archivos(uploaded_files, combinar=True)
        
        if df is not None and len(df) > 0:
            # Filtrar filas inválidas
            df = df[df['categoria_completa'].notnull()].copy()
            
            if len(df) > 0:
                # 1. Exportar Excel de categorías
                excel_categorias = agrupador.exportar_categorias_unico_excel(df, carpeta_salida)
                
                # 2. Identificar y exportar solos
                df_solos = agrupador.identificar_solos(df)
                excel_solos = agrupador.exportar_solos(df_solos, carpeta_salida)
                
                # 3. Generar brackets
                carpeta_brackets = os.path.join(carpeta_salida, "brackets")
                resultado_brackets = generar_brackets_desde_excel(excel_categorias, carpeta_brackets)
                
                # 4. Generar resumen
                generar_resumen_torneo(df, df_solos, resultado_brackets, carpeta_salida)
                
                resultado = {
                    'success': True,
                    'participantes': len(df),
                    'solos': len(df_solos),
                    'brackets': len(resultado_brackets['imagenes']) if resultado_brackets else 0,
                    'pdf': resultado_brackets['pdf'] if resultado_brackets else None
                }
            else:
                resultado = {'success': False, 'error': 'No quedan filas válidas para procesar'}
        else:
            resultado = {'success': False, 'error': 'No se pudieron procesar participantes'}
        
        # Preparar respuesta con información de resultados
        response_data = {
            'success': True,
            'message': 'Torneo procesado exitosamente',
            'timestamp': timestamp,
            'files_processed': len(uploaded_files),
            'output_folder': carpeta_salida,
            'result_files': []
        }
        
        # Listar archivos generados
        if os.path.exists(carpeta_salida):
            for root, dirs, files in os.walk(carpeta_salida):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), carpeta_salida)
                    response_data['result_files'].append(rel_path)
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Error procesando archivos: {str(e)}"
        print(f"Error: {error_msg}")
        print(traceback.format_exc())
        return jsonify({'error': error_msg}), 500

@app.route('/download/<timestamp>/<filename>')
def download_file(timestamp, filename):
    try:
        carpeta_salida = os.path.join(app.config['RESULTS_FOLDER'], f'torneo_{timestamp}')
        file_path = os.path.join(carpeta_salida, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'Archivo no encontrado'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Error descargando archivo: {str(e)}'}), 500

@app.route('/download-all/<timestamp>')
def download_all(timestamp):
    try:
        carpeta_salida = os.path.join(app.config['RESULTS_FOLDER'], f'torneo_{timestamp}')
        
        if not os.path.exists(carpeta_salida):
            return jsonify({'error': 'Carpeta de resultados no encontrada'}), 404
        
        # Crear archivo ZIP con todos los resultados
        zip_path = os.path.join(app.config['RESULTS_FOLDER'], f'torneo_completo_{timestamp}.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(carpeta_salida):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, carpeta_salida)
                    zipf.write(file_path, arcname)
        
        return send_file(zip_path, as_attachment=True, download_name=f'torneo_completo_{timestamp}.zip')
        
    except Exception as e:
        return jsonify({'error': f'Error creando archivo ZIP: {str(e)}'}), 500

@app.route('/status')
def status():
    return jsonify({
        'status': 'running',
        'version': '0.5',
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'results_folder': app.config['RESULTS_FOLDER']
    })

if __name__ == '__main__':
    print("🚀 Iniciando FILO 0.5 Web App...")
    print("📁 Carpeta de uploads:", app.config['UPLOAD_FOLDER'])
    print("📁 Carpeta de resultados:", app.config['RESULTS_FOLDER'])
    print("🌐 Servidor disponible en: http://localhost:5000")
    
    # Obtener puerto de variables de entorno (Heroku)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 