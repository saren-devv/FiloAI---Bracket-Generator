#!/usr/bin/env python3
"""
FILO 0.5 Web App - Interfaz web para gestión de torneos de Taekwondo
Autor: AI Assistant
Fecha: 2024
"""

import sys
import subprocess
import os

# Intentar importar Flask-CORS, si falla, instalarlo
try:
    from flask_cors import CORS
except ImportError:
    print("Flask-CORS no encontrado, instalando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask-CORS"])
    from flask_cors import CORS

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import tempfile
import shutil
from pathlib import Path
import zipfile
from datetime import datetime
import traceback

# Importar la lógica existente
from filo_0_5 import AgrupadorMultiple, generar_brackets_desde_excel, generar_resumen_torneo
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# 🎨 ESTILO MEXXUS ARENA
MEXXUS_COLORS = {
    'gold': colors.Color(0.85, 0.65, 0.125),        # Dorado Mexxus
    'dark_gold': colors.Color(0.72, 0.53, 0.04),    # Dorado oscuro
    'red_fighter': colors.Color(0.8, 0.15, 0.15),   # Rojo luchador
    'blue_fighter': colors.Color(0.15, 0.35, 0.8),  # Azul luchador
    'dark_gray': colors.Color(0.2, 0.2, 0.2),       # Gris oscuro
    'light_gray': colors.Color(0.95, 0.95, 0.95)    # Gris claro
}

app = Flask(__name__)
CORS(app)

# Importar configuración
from config import get_config

# Configuración
config = get_config()
app.config.from_object(config)

# Crear carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/upload')
def upload_page():
    return render_template('index.html')

@app.route('/editor')
def editor():
    return render_template('editor.html')

@app.route('/generator')
def generator():
    return render_template('editor.html')

@app.route('/bracket_templates/<filename>')
def serve_bracket_template(filename):
    """Sirve las plantillas de brackets estáticamente."""
    return send_from_directory('bracket_templates', filename)

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
                
                # Preparar respuesta con información de resultados
                response_data = {
                    'success': True,
                    'message': 'Torneo procesado exitosamente',
                    'timestamp': timestamp,
                    'files_processed': len(uploaded_files),
                    'participantes': len(df),
                    'solos': len(df_solos),
                    'brackets': len(resultado_brackets['imagenes']) if resultado_brackets else 0,
                    'output_folder': carpeta_salida,
                    'result_files': []
                }
            else:
                response_data = {'success': False, 'error': 'No quedan filas válidas para procesar'}
        else:
            response_data = {'success': False, 'error': 'No se pudieron procesar participantes'}
        
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

# === NUEVAS RUTAS PARA EDITOR VISUAL ===

@app.route('/api/brackets', methods=['GET'])
def get_brackets():
    """Obtiene todos los brackets creados."""
    # TODO: Implementar base de datos para brackets
    return jsonify({'brackets': []})

@app.route('/api/brackets', methods=['POST'])
def create_bracket():
    """Crea un nuevo bracket vacío."""
    data = request.get_json()
    bracket_id = f"bracket_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Estructura básica de un bracket
    bracket = {
        'id': bracket_id,
        'name': data.get('name', 'Nuevo Bracket'),
        'category': data.get('category', ''),
        'participants': [],
        'structure': data.get('structure', 'single_elimination'),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    # TODO: Guardar en base de datos
    return jsonify({'bracket': bracket})

@app.route('/api/brackets/<bracket_id>', methods=['GET'])
def get_bracket(bracket_id):
    """Obtiene un bracket específico."""
    # TODO: Obtener de base de datos
    return jsonify({'bracket': None})

@app.route('/api/brackets/<bracket_id>', methods=['PUT'])
def update_bracket(bracket_id):
    """Actualiza un bracket específico."""
    data = request.get_json()
    # TODO: Actualizar en base de datos
    return jsonify({'success': True})

@app.route('/api/brackets/<bracket_id>/participants', methods=['POST'])
def add_participant(bracket_id):
    """Añade un participante a un bracket."""
    data = request.get_json()
    participant = {
        'id': f"participant_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
        'name': data.get('name', ''),
        'academy': data.get('academy', ''),
        'position': data.get('position', {'x': 0, 'y': 0})
    }
    # TODO: Añadir a base de datos
    return jsonify({'participant': participant})

@app.route('/api/brackets/<bracket_id>/participants/<participant_id>', methods=['DELETE'])
def remove_participant(bracket_id, participant_id):
    """Elimina un participante de un bracket."""
    # TODO: Eliminar de base de datos
    return jsonify({'success': True})

@app.route('/api/brackets/<bracket_id>/participants/<participant_id>', methods=['PUT'])
def update_participant(bracket_id, participant_id):
    """Actualiza la posición o datos de un participante."""
    data = request.get_json()
    # TODO: Actualizar en base de datos
    return jsonify({'success': True})

def detect_excel_columns(df):
    """
    Detecta automáticamente las columnas del Excel basándose en patrones flexibles.
    Retorna un diccionario con las columnas encontradas.
    """
    detected_columns = {}
    
    # Convertir nombres de columnas a minúsculas para búsqueda
    columnas_lower = {col.lower(): col for col in df.columns}
    
    # Patrones de búsqueda para cada campo requerido
    patterns = {
        'nombre': ['nombre', 'name', 'first_name', 'firstname'],
        'apellido': ['apellido', 'lastname', 'last_name', 'surname'],
        'documento': ['documento', 'dni', 'cedula', 'cédula', 'id', 'identificacion', 'identificación', 'pasaporte', 'ci'],
        'fecha_nacimiento': ['nacim', 'fecha', 'birth', 'nacimiento', 'fecha_nacimiento', 'birthdate', 'born'],
        'genero': ['sexo', 'genero', 'género', 'gender', 'sex'],
        'kup': ['kup', 'dan', 'nivel', 'grado', 'cinturon', 'cinturón', 'belt', 'grade'],
        'peso': ['peso', 'weight', 'kg', 'kilos'],
        'modalidad': ['modalidad', 'modality', 'disciplina', 'discipline', 'category', 'tipo', 'sport'],
        'abreviatura': ['abreviatura', 'abbreviation', 'abrev', 'academia', 'academy', 'club', 'escuela', 'school', 'team']
    }
    
    # Buscar cada patrón
    for field, field_patterns in patterns.items():
        detected_columns[field] = None
        for pattern in field_patterns:
            found_col = None
            for col_lower, col_original in columnas_lower.items():
                if pattern in col_lower:
                    found_col = col_original
                    break
            if found_col:
                detected_columns[field] = found_col
                break
    
    return detected_columns



@app.route('/api/process-file', methods=['POST'])
def process_file_for_editor():
    """Procesa un archivo Excel y devuelve datos estructurados para el editor."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Archivo no válido'}), 400
        
        # Guardar archivo temporalmente
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_{timestamp}')
        os.makedirs(temp_folder, exist_ok=True)
        
        filepath = os.path.join(temp_folder, file.filename)
        file.save(filepath)
        
        # Leer Excel directamente
        print(f"📊 Procesando archivo: {file.filename}")
        df_raw = pd.read_excel(filepath)
        print(f"📋 Filas totales en Excel: {len(df_raw)}")
        print(f"📋 Columnas encontradas: {list(df_raw.columns)}")
        
        # Detectar columnas automáticamente
        detected_cols = detect_excel_columns(df_raw)
        print(f"🔍 Columnas detectadas: {detected_cols}")
        
        # Mostrar estadísticas de modalidad si existe
        if detected_cols['modalidad']:
            modalidades = df_raw[detected_cols['modalidad']].value_counts()
            print(f"📊 Distribución de modalidades:")
            for modalidad, count in modalidades.items():
                print(f"  • {modalidad}: {count} atletas")
        
        # Verificar columnas requeridas
        required_fields = ['fecha_nacimiento', 'genero', 'kup', 'peso']
        missing_required = [field for field in required_fields if not detected_cols[field]]
        
        if missing_required:
            return jsonify({
                'error': f'Columnas requeridas faltantes: {", ".join(missing_required)}',
                'columns_found': list(df_raw.columns),
                'columns_detected': detected_cols
            }), 400
        
        # Usar directamente el AgrupadorMultiple sin modificar el archivo
        # El AgrupadorMultiple ya tiene patrones de búsqueda flexibles
        agrupador = AgrupadorMultiple()
        df = agrupador.procesar_multiples_archivos([filepath], combinar=True)
        
        print(f"🔄 Procesamiento completado. Filas obtenidas: {len(df) if df is not None else 0}")
        
        # Filtrar por modalidad KYORUGUI después del procesamiento si está disponible
        if detected_cols['modalidad'] and df is not None and len(df) > 0:
            print(f"🥋 Filtrando participantes de modalidad KYORUGUI...")
            # Leer el Excel original para hacer el filtrado
            df_original = pd.read_excel(filepath)
            
            # Mostrar modalidades antes del filtrado
            modalidades_antes = df_original[detected_cols['modalidad']].astype(str).str.upper().str.strip().value_counts()
            print(f"📊 Modalidades antes del filtrado:")
            for modalidad, count in modalidades_antes.items():
                print(f"  • '{modalidad}': {count} atletas")
            
            kyorugui_mask = df_original[detected_cols['modalidad']].astype(str).str.upper().str.strip().isin(
                ['KYORUGUI', 'KYORUGI', 'COMBATE', 'SPARRING', 'LUCHA']
            )
            
            # Mostrar qué modalidades se van a excluir
            modalidades_excluidas = df_original[~kyorugui_mask][detected_cols['modalidad']].astype(str).str.upper().str.strip().value_counts()
            if len(modalidades_excluidas) > 0:
                print(f"❌ Modalidades excluidas:")
                for modalidad, count in modalidades_excluidas.items():
                    print(f"  • '{modalidad}': {count} atletas")
            
            # Aplicar el filtro al DataFrame procesado
            df = df.iloc[kyorugui_mask.values].copy()
            excluded_count = len(df_original) - len(df)
            print(f"✅ {len(df)} participantes KYORUGUI incluidos, {excluded_count} excluidos")
        
        if df is not None and len(df) > 0:
            # Mostrar información antes del filtrado de categorías
            print(f"📊 Antes del filtrado de categorías: {len(df)} participantes")
            
            # Contar cuántos tienen categoría nula
            sin_categoria = df[df['categoria_completa'].isnull()]
            if len(sin_categoria) > 0:
                print(f"⚠️ {len(sin_categoria)} participantes sin categoría válida (serán excluidos):")
                for idx, row in sin_categoria.head(5).iterrows():  # Mostrar solo los primeros 5
                    print(f"  • Fila {idx}: edad={row.get('edad')}, sexo={row.get('sexo_normalizado')}, nivel={row.get('nivel_normalizado')}, peso={row.get('categoria_peso')}")
                if len(sin_categoria) > 5:
                    print(f"  ... y {len(sin_categoria) - 5} más")
            
            # Filtrar filas válidas
            df = df[df['categoria_completa'].notnull()].copy()
            print(f"📊 Después del filtrado de categorías: {len(df)} participantes")
            
            # Agrupar por categoría
            categories_data = {}
            for categoria in df['categoria_completa'].unique():
                participants_in_cat = df[df['categoria_completa'] == categoria]
                
                participants = []
                for _, row in participants_in_cat.iterrows():
                    # Construir nombre completo usando columnas detectadas
                    full_name = ""
                    if detected_cols['nombre'] and detected_cols['apellido']:
                        full_name = f"{row[detected_cols['nombre']]} {row[detected_cols['apellido']]}"
                    elif detected_cols['nombre']:
                        full_name = str(row[detected_cols['nombre']])
                    else:
                        # Fallback: buscar cualquier columna que pueda contener nombre
                        for col in df.columns:
                            if 'nombre' in col.lower():
                                full_name = str(row[col])
                                break
                        if not full_name:
                            full_name = f"Participante {row.name}"
                    
                    # Obtener abreviación de academia
                    academy = ""
                    if detected_cols['abreviatura'] and row[detected_cols['abreviatura']]:
                        academy = str(row[detected_cols['abreviatura']]).strip()
                    
                    # Obtener documento si está disponible
                    document = ""
                    if detected_cols['documento'] and row[detected_cols['documento']]:
                        document = str(row[detected_cols['documento']]).strip()
                    
                    participants.append({
                        'name': full_name,
                        'academy': academy,
                        'document': document,
                        'age': row.get('edad'),
                        'weight': row.get('categoria_peso'),
                        'level': row.get('nivel_normalizado'),
                        'gender': row.get('sexo_normalizado')
                    })
                
                categories_data[categoria] = {
                    'name': categoria,
                    'participants': participants,
                    'count': len(participants)
                }
            
            # Limpiar archivo temporal
            shutil.rmtree(temp_folder, ignore_errors=True)
            
            return jsonify({
                'success': True,
                'categories': categories_data,
                'total_participants': len(df),
                'total_categories': len(categories_data),
                'detected_columns': detected_cols,
                'file_info': {
                    'filename': file.filename,
                    'original_rows': len(df_raw),
                    'processed_rows': len(df)
                }
            })
        else:
            return jsonify({'error': 'No se pudieron procesar participantes válidos'}), 400
            
    except Exception as e:
        print(f"Error procesando archivo: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error procesando archivo: {str(e)}'}), 500

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf_from_editor():
    """Genera PDF desde los brackets del editor visual."""
    try:
        print("🔄 Iniciando generación de PDF...")
        
        data = request.get_json()
        if not data:
            print("❌ No se recibieron datos JSON")
            return jsonify({'error': 'No se recibieron datos'}), 400
            
        brackets_data = data.get('brackets', [])
        print(f"📄 Generando PDF para {len(brackets_data)} brackets")
        print(f"📊 Primer bracket (ejemplo): {brackets_data[0] if brackets_data else 'Sin datos'}")
        
        if not brackets_data:
            return jsonify({'error': 'No hay brackets para generar PDF'}), 400
        
        # Crear archivo temporal Excel para usar con el sistema existente
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'editor_pdf_{timestamp}')
        os.makedirs(temp_folder, exist_ok=True)
        
        # Crear DataFrame con los datos de los brackets
        all_participants = []
        for bracket in brackets_data:
            category = bracket['category'] or bracket.get('name', '')
            print(f"📊 Procesando bracket '{category}' con {len(bracket['participants'])} participantes")
            
            # Deduplicar participantes por nombre y categoría
            seen_participants = set()
            unique_participants = []
            
            for participant in bracket['participants']:
                # Manejar diferentes estructuras de participantes
                if isinstance(participant, str):
                    nombre = participant
                    abreviatura = ''
                elif isinstance(participant, dict):
                    nombre = participant.get('name', '')
                    abreviatura = participant.get('academy', '')
                else:
                    nombre = str(participant)
                    abreviatura = ''
                
                # Crear clave única para deduplicación
                participant_key = (nombre.strip().upper(), category, abreviatura.strip().upper())
                
                if participant_key not in seen_participants:
                    seen_participants.add(participant_key)
                    unique_participants.append({
                        'Nombre': nombre,
                        'Apellido': '',
                        'categoria_completa': category,
                        'Abreviatura': abreviatura
                    })
            
            all_participants.extend(unique_participants)
            print(f"✅ Bracket '{category}': {len(unique_participants)} participantes únicos (de {len(bracket['participants'])} originales)")
        
        if not all_participants:
            return jsonify({'error': 'No hay participantes en los brackets'}), 400
        
        print(f"📊 {len(all_participants)} participantes procesados para PDF")
        df = pd.DataFrame(all_participants)
        print(f"📋 DataFrame creado: {df.shape} - Columnas: {list(df.columns)}")
        
        # Crear Excel temporal
        excel_path = os.path.join(temp_folder, 'brackets_temp.xlsx')
        try:
            df.to_excel(excel_path, index=False)
            print(f"✅ Excel temporal creado: {excel_path}")
        except Exception as e:
            print(f"❌ Error creando Excel: {e}")
            raise
        
        # Generar PDF usando el nuevo sistema sin plantillas
        print(f"🎨 Generando PDF con líneas dinámicas (sin plantillas)...")
        
        try:
            # Usar una función nueva que genere PDF con líneas dinámicas
            pdf_path = generate_dynamic_brackets_pdf(all_participants, temp_folder, timestamp)
            print(f"🏆 PDF dinámico generado: {pdf_path}")
            
            if pdf_path and os.path.exists(pdf_path):
                return send_file(pdf_path, as_attachment=True, 
                               download_name=f'brackets_editor_{timestamp}.pdf')
            else:
                return jsonify({'error': 'Error generando PDF dinámico'}), 500
                
        except Exception as e:
            print(f"❌ Error generando PDF dinámico: {e}")
            import traceback
            traceback.print_exc()
            raise

            
    except Exception as e:
        print(f"❌ Error generando PDF desde editor: {e}")
        import traceback
        traceback.print_exc()
        
        # Información adicional para debug
        if 'data' in locals():
            print(f"📊 Datos recibidos: {data}")
        if 'brackets_data' in locals():
            print(f"📊 Brackets data: {len(brackets_data) if brackets_data else 0} brackets")
        if 'all_participants' in locals():
            print(f"📊 Participantes procesados: {len(all_participants)}")
            
        return jsonify({'error': f'Error generando PDF: {str(e)}'}), 500
    finally:
        # Limpiar archivos temporales
        try:
            if 'temp_folder' in locals():
                print(f"🧹 Limpiando archivos temporales: {temp_folder}")
                shutil.rmtree(temp_folder, ignore_errors=True)
        except Exception as cleanup_error:
            print(f"⚠️ Error limpiando archivos: {cleanup_error}")

def generate_dynamic_brackets_pdf(participants_data, temp_folder, timestamp):
    """
    Genera un PDF con brackets usando líneas dinámicas (sin plantillas PNG)
    Similar al renderizado del editor visual
    """
    try:
        pdf_path = os.path.join(temp_folder, f'brackets_dynamic_{timestamp}.pdf')
        
        # Crear el PDF
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # Agrupar participantes por categoría
        categories = {}
        for participant in participants_data:
            category = participant['categoria_completa']
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'name': participant['Nombre'],
                'academy': participant['Abreviatura']
            })
        
        print(f"📊 Generando PDF para {len(categories)} categorías")
        
        # 📄 UNA PÁGINA POR BRACKET - Estilo Mexxus Arena
        for i, (category_name, participants) in enumerate(categories.items()):
            print(f"🏷️ Dibujando categoría: {category_name} ({len(participants)} participantes)")
            
            # Nueva página para cada bracket (excepto el primero)
            if i > 0:
                c.showPage()
            
            # Posición inicial centrada en la página
            y_position = height - 100  # Más espacio desde arriba
            
            # Título de la categoría - Estilo Mexxus Arena centrado
            c.setFillColor(MEXXUS_COLORS['gold'])
            c.setFont("Helvetica-Bold", 18)  # Más grande para página individual
            title_width = c.stringWidth(category_name, "Helvetica-Bold", 18)
            x_centered = (width - title_width) / 2  # Centrar título
            c.drawString(x_centered, y_position, category_name)
            c.setFillColor(colors.black)  # Restaurar color negro
            y_position -= 60  # Más espacio después del título
            
            # Centrar bracket horizontalmente en la página (ajustado para cajas más anchas)
            bracket_x = (width - 550) / 2  # Centrar bracket (550px de ancho aprox) - aumentado de 450
            
            # Dibujar bracket centrado
            if len(participants) == 1:
                # Un solo participante
                draw_single_participant(c, bracket_x, y_position, participants[0])
                
            elif len(participants) == 2:
                # Dos participantes conectados
                draw_two_participants_bracket(c, bracket_x, y_position, participants)
                
            elif len(participants) == 3:
                # Tres participantes (dos + bye)
                draw_three_participants_bracket(c, bracket_x, y_position, participants)
                
            else:
                # Cuatro o más participantes
                draw_multiple_participants_bracket(c, bracket_x, y_position, participants)
        
        c.save()
        print(f"✅ PDF dinámico generado: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        print(f"❌ Error generando PDF dinámico: {e}")
        raise

def draw_single_participant(c, x, y, participant):
    """Dibuja un participante solo - Estilo Mexxus Arena"""
    # Participante único con color azul (primera ronda)
    draw_participant_box(c, x, y, participant, 0, is_first_round=True)

def draw_two_participants_bracket(c, x, y, participants):
    """Dibuja bracket de 2 participantes con línea conectora - Estilo Mexxus Arena"""
    # PRIMERA RONDA: Participantes con colores azul/rojo
    draw_participant_box(c, x, y, participants[0], 0, is_first_round=True)      # Azul
    draw_participant_box(c, x, y-40, participants[1], 1, is_first_round=True)   # Rojo
    
    # 🥇 TODAS LAS LÍNEAS DORADAS - Estilo Mexxus Arena (ajustadas para cajas más anchas)
    c.setStrokeColor(MEXXUS_COLORS['gold'])
    c.setLineWidth(2)
    c.line(x+280, y-7.5, x+330, y-7.5)       # Desde participante 1 (centro) - ajustado de 200 a 280
    c.line(x+280, y-47.5, x+330, y-47.5)     # Desde participante 2 (centro) - ajustado de 200 a 280
    
    # Línea vertical conectora
    c.line(x+330, y-7.5, x+330, y-47.5)      # ajustado de 250 a 330
    
    # Línea hacia el ganador (desde el punto medio) - sin caja final
    c.line(x+330, y-27.5, x+430, y-27.5)     # ajustado de 250/350 a 330/430
    
    # Restaurar configuración por defecto
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)

def draw_three_participants_bracket(c, x, y, participants):
    """Dibuja bracket de 3 participantes siguiendo estructura de plantilla - Estilo Mexxus Arena"""
    # PRIMERA RONDA: Solo estos participantes con colores azul/rojo
    draw_participant_box(c, x, y-80, participants[0], 0, is_first_round=True)   # Azul
    draw_participant_box(c, x, y-120, participants[1], 1, is_first_round=True)  # Rojo
    draw_participant_box(c, x, y-40, participants[2], 2, is_first_round=True)   # Azul (bye)
    
    # 🥇 APLICAR ESTILO DORADO PARA TODAS LAS LÍNEAS (ajustadas para cajas más anchas)
    c.setStrokeColor(MEXXUS_COLORS['gold'])
    c.setLineWidth(2)
    
    # PRIMERA RONDA: Conexión de los dos primeros participantes
    c.line(x+280, y-87.5, x+330, y-87.5)      # Línea desde participante 1 (centro) - ajustado de 200 a 280
    c.line(x+280, y-127.5, x+330, y-127.5)    # Línea desde participante 2 (centro) - ajustado de 200 a 280
    c.line(x+330, y-87.5, x+330, y-127.5)     # Línea vertical conectora - ajustado de 250 a 330
    
    # Línea horizontal hacia semifinal (desde el medio de la conexión)
    c.line(x+330, y-107.5, x+430, y-107.5)    # Hacia punto de semifinal - ajustado de 250/350 a 330/430
    
    # SEGUNDA RONDA: Línea del bye hacia el punto de semifinal
    c.line(x+280, y-47.5, x+430, y-47.5)      # Línea directa del bye - ajustado de 200/350 a 280/430
    
    # CONEXIÓN FINAL: Unir semifinal y bye hacia final - sin cajas
    c.line(x+430, y-47.5, x+430, y-107.5)     # Línea vertical conectora - ajustado de 350 a 430
    c.line(x+430, y-77.5, x+530, y-77.5)      # Línea horizontal hacia final - ajustado de 350/450 a 430/530
    
    # Restaurar configuración por defecto
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)

def draw_multiple_participants_bracket(c, x, y, participants):
    """Dibuja bracket de 4+ participantes con estructura de eliminación - Estilo Mexxus Arena"""
    participant_height = 25
    spacing = 10
    
    # 🥇 TODAS LAS LÍNEAS DORADAS - Estilo Mexxus Arena
    c.setStrokeColor(MEXXUS_COLORS['gold'])
    c.setLineWidth(2)
    
    # Dibujar participantes en la primera ronda - Solo esta ronda con colores azul/rojo
    for i, participant in enumerate(participants[:8]):  # Máximo 8 para que quepa
        participant_y = y - (i * (participant_height + spacing))
        draw_participant_box(c, x, participant_y, participant, i, is_first_round=True)  # Solo primera ronda colorida
        
        # Líneas de conexión por pares (ajustadas para cajas más anchas)
        if i % 2 == 1:  # Cada segundo participante
            # Conectar con el participante anterior
            prev_y = y - ((i-1) * (participant_height + spacing))
            current_y = participant_y
            # Líneas horizontales - ajustado de 200 a 280
            c.line(x+280, prev_y-10, x+330, prev_y-10)
            c.line(x+280, current_y-10, x+330, current_y-10)
            
            # Línea vertical - ajustado de 250 a 330
            c.line(x+330, prev_y-10, x+330, current_y-10)
            
            # Línea hacia siguiente ronda - ajustado de 250/300 a 330/380
            middle_y = (prev_y + current_y) / 2 - 10
            c.line(x+330, middle_y, x+380, middle_y)
    
    # Restaurar configuración por defecto al final
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)

def draw_participant_box(c, x, y, participant, position_index=0, is_first_round=True):
    """Dibuja una caja de participante con nombre y academia - Estilo Mexxus Arena"""
    name_with_academy = f"{participant['name']}"
    if participant['academy']:
        name_with_academy += f" ({participant['academy']})"
    
    # Truncar si es muy largo (aumentamos el límite)
    if len(name_with_academy) > 50:
        name_with_academy = name_with_academy[:47] + "..."
    
    # 🎨 CUADRO BASE: Siempre gris claro - MÁS ANCHO
    base_fill_color = MEXXUS_COLORS['light_gray']
    text_color = MEXXUS_COLORS['dark_gray']
    
    # Dibujar cuadro base (gris claro) - Aumentamos ancho de 200 a 280
    c.setFillColor(base_fill_color)
    c.setStrokeColor(MEXXUS_COLORS['dark_gold'])
    c.setLineWidth(1.5)
    c.rect(x, y-20, 280, 25, fill=1, stroke=1)
    
    if is_first_round:
        # 🎨 FRANJA LATERAL: Solo una pequeña parte azul/roja al inicio
        if position_index % 2 == 0:
            accent_color = MEXXUS_COLORS['blue_fighter']  # Azul
        else:
            accent_color = MEXXUS_COLORS['red_fighter']   # Rojo
        
        # Dibujar franja lateral izquierda (10px de ancho)
        c.setFillColor(accent_color)
        c.rect(x, y-20, 10, 25, fill=1, stroke=0)  # Franja de 10px sin borde
    
    # Texto con fuente más pequeña y sin negrita
    c.setFillColor(text_color)
    c.setFont("Helvetica", 9)
    c.drawString(x+15, y-13, name_with_academy)  # Mover texto 10px a la derecha
    
    # Restaurar solo el color de relleno (no interferir con líneas)
    c.setFillColor(colors.black)
    # NO restaurar setStrokeColor ni setLineWidth para no interferir con líneas doradas



if __name__ == '__main__':
    print("🚀 Iniciando FILO 0.5 Web App...")
    print("📁 Carpeta de uploads:", app.config['UPLOAD_FOLDER'])
    print("📁 Carpeta de resultados:", app.config['RESULTS_FOLDER'])
    print("🌐 Servidor disponible en: http://localhost:5000")
    
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    ) 