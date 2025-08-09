#!/usr/bin/env python3
"""
FILO 0.5-beta - Script autocontenible para gestión de torneos de Taekwondo
Incluye: procesamiento de participantes, generación de brackets, PDF, excels y resumen.
Autor: AI Assistant
Fecha: 2024
"""

import pandas as pd
import json
import os
import re
from datetime import datetime, date
from pathlib import Path
import glob
import shutil
import sys
import tempfile
import time

# --- UTILIDADES DE CATEGORÍAS ---
def load_categories():
    """Carga las categorías desde el archivo JSON."""
    try:
        with open('categorias_taekwondo.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo categorias_taekwondo.json")
        return None

def generate_category_combinations(categories):
    """Genera todas las combinaciones posibles de categorías (formato clásico)."""
    all_combinations = []
    for division, data in categories.items():
        niveles = data['NIVEL']
        # Para CADETE, JUVENIL, MAYORES: pesos por sexo
        if isinstance(data['SEXO'], dict):
            for nivel in niveles:
                for genero, pesos in data['SEXO'].items():
                    for peso in pesos:
                        categoria = f"{nivel} {division.replace('_', ' ')} {genero} {peso}"
                        all_combinations.append(categoria)
        else:
            # Para divisiones con pesos mixtos
            for nivel in niveles:
                for genero in data['SEXO']:
                    for peso in data['PESOS']:
                        categoria = f"{nivel} {division.replace('_', ' ')} {genero} {peso}"
                        all_combinations.append(categoria)
    return sorted(all_combinations)

def validate_categories(df_participantes):
    """
    Valida que todas las categorías generadas estén en las oficiales.
    """
    categories = load_categories()
    if not categories:
        raise Exception("No se pudieron cargar las categorías oficiales.")
    valid_categories = generate_category_combinations(categories)
    participant_categories = df_participantes['categoria_completa'].unique()
    # Filtrar None y categorías inválidas
    invalid_categories = [cat for cat in participant_categories if cat is None or cat not in valid_categories]
    return len(invalid_categories) == 0, invalid_categories

# --- CLASE BASE DE AGRUPAMIENTO ---
class AgrupadorTaekwondo:
    """Clase principal para agrupar participantes de taekwondo según criterios oficiales."""
    def __init__(self, archivo_categorias="categorias_taekwondo.json"):
        self.categorias = self._cargar_categorias(archivo_categorias)
        self.mapeo_niveles = {
            "10": "Festival", "9": "Festival", "8": "Festival", "7": "Festival",
            "6": "Noveles", "5": "Noveles", "4": "Noveles", "3": "Noveles",
            "2": "Avanzados", "1": "Avanzados"
        }
        # Mapeo adicional para niveles especiales
        self.mapeo_niveles_especiales = {
            "Intermedios": "Noveles"  # Mapear Intermedios a Noveles
        }
    def _cargar_categorias(self, archivo):
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Error al cargar categorías: {e}")
    def calcular_edad(self, fecha_nacimiento):
        if pd.isna(fecha_nacimiento):
            return None
        try:
            if isinstance(fecha_nacimiento, str):
                formatos = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
                for formato in formatos:
                    try:
                        fecha_nacimiento = datetime.strptime(fecha_nacimiento, formato)
                        break
                    except ValueError:
                        continue
                else:
                    return None
            if isinstance(fecha_nacimiento, datetime):
                fecha_nacimiento = fecha_nacimiento.date()
            elif hasattr(fecha_nacimiento, 'date'):
                fecha_nacimiento = fecha_nacimiento.date()
            hoy = date.today()
            edad = hoy.year - fecha_nacimiento.year
            if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
                edad -= 1
            return edad
        except Exception:
            return None
    def normalizar_kup_dan(self, kup_dan):
        if pd.isna(kup_dan):
            return "Festival"
        kup_dan_str = str(kup_dan).upper().strip()
        
        # Mapeo más flexible para niveles
        nivel_variantes = {
            # Festival
            'FESTIVAL': 'Festival',
            'PRINCIPIANTE': 'Festival',
            'INICIAL': 'Festival',
            'BLANCO': 'Festival',
            'AMARILLO': 'Festival',
            'BLANCO AMARILLO': 'Festival',
            'AMARILLO VERDE': 'Festival',
            
            # Noveles
            'NOVELES': 'Noveles',
            'NOVEL': 'Noveles',
            'INTERMEDIO': 'Noveles',
            'VERDE': 'Noveles',
            'AZUL': 'Noveles',
            'VERDE AZUL': 'Noveles',
            'AZUL ROJO': 'Noveles',
            
            # Avanzados
            'AVANZADOS': 'Avanzados',
            'AVANZADO': 'Avanzados',
            'ROJO': 'Avanzados',
            'NEGRO': 'Avanzados',
            'ROJO NEGRO': 'Avanzados'
        }
        
        # Verificar variantes de texto
        if kup_dan_str in nivel_variantes:
            return nivel_variantes[kup_dan_str]
        
        # Verificar si es un nivel especial
        if kup_dan_str in self.mapeo_niveles_especiales:
            return self.mapeo_niveles_especiales[kup_dan_str]
        
        # Buscar DAN
        if 'DAN' in kup_dan_str:
            return "Avanzados"
        
        # Extraer números para KUP
        numeros = re.findall(r'\d+', kup_dan_str)
        if numeros:
            numero = numeros[0]
            return self.mapeo_niveles.get(numero, "Festival")
        
        return "Festival"
    def normalizar_sexo(self, sexo):
        if pd.isna(sexo):
            return None
        sexo_str = str(sexo).upper().strip()
        
        # Mapeo más flexible para masculino
        masculino_variantes = ['M', 'MASCULINO', 'MALE', 'HOMBRE', 'H', 'MASC', 'MASCULINOS', 'VARON', 'VARÓN']
        if sexo_str in masculino_variantes:
            return "MASCULINO"
        
        # Mapeo más flexible para femenino
        femenino_variantes = ['F', 'FEMENINO', 'FEMALE', 'MUJER', 'FEM', 'FEMENINOS', 'DAMA', 'DAMAS']
        if sexo_str in femenino_variantes:
            return "FEMENINO"
        
        return None
    def determinar_categoria_edad(self, edad):
        if edad is None:
            return None
        
        # Mapeo de rangos de edad según el formato del JSON
        rangos_edad = {
            'PRE_INFANTIL': (4, 6),
            'INFANTIL_A': (7, 8),
            'INFANTIL_B': (9, 10),
            'INFANTIL_C': (11, 12),
            'CADETE': (12, 14),
            'JUVENIL': (15, 17),
            'MAYORES': (18, 100)
        }
        
        for categoria, (edad_min, edad_max) in rangos_edad.items():
            if edad_min <= edad <= edad_max:
                return categoria
        return None

    def determinar_categoria_peso(self, peso, categoria_edad, sexo):
        if peso is None or categoria_edad is None or sexo is None:
            return None
        try:
            peso = float(peso)
        except:
            return None
        criterios = self.categorias[categoria_edad]
        # Pesos por sexo (CADETE, JUVENIL, MAYORES)
        if isinstance(criterios.get('SEXO'), dict) and sexo.upper() in criterios['SEXO']:
            rangos_peso = criterios['SEXO'][sexo.upper()]
        else:
            rangos_peso = criterios['PESOS']
        for peso_cat in rangos_peso:
            if '-' in peso_cat:
                lim = float(peso_cat.replace('-', ''))
                if peso <= lim:
                    return peso_cat
            elif '+' in peso_cat:
                lim = float(peso_cat.replace('+', ''))
                if peso > lim:
                    return peso_cat
        return None

    def procesar_participantes(self, archivo_excel):
        try:
            df = pd.read_excel(archivo_excel)
        except Exception as e:
            print(f"❌ Error leyendo {archivo_excel}: {e}")
            return None
        
        # Búsqueda más flexible de columnas
        columnas_lower = [c.lower() for c in df.columns]
        
        # Buscar columna de fecha de nacimiento
        col_fecha = None
        for patron in ['nacim', 'fecha', 'birth', 'nacimiento']:
            col_fecha = next((c for c in df.columns if patron in c.lower()), None)
            if col_fecha:
                break
        
        # Buscar columna de sexo
        col_sexo = None
        for patron in ['sexo', 'genero', 'género', 'gender', 'sex']:
            col_sexo = next((c for c in df.columns if patron in c.lower()), None)
            if col_sexo:
                break
        
        # Buscar columna de nivel
        col_kup = None
        for patron in ['kup', 'dan', 'nivel', 'grado', 'cinturon', 'cinturón', 'belt']:
            col_kup = next((c for c in df.columns if patron in c.lower()), None)
            if col_kup:
                break
        
        # Buscar columna de peso
        col_peso = None
        for patron in ['peso', 'weight', 'kg', 'kilos']:
            col_peso = next((c for c in df.columns if patron in c.lower()), None)
            if col_peso:
                break
        
        # Buscar columna de abreviación (opcional)
        col_abreviatura = None
        for patron in ['abreviatura', 'abbreviation', 'abrev', 'academia']:
            col_abreviatura = next((c for c in df.columns if patron in c.lower()), None)
            if col_abreviatura:
                break
        
        if not all([col_fecha, col_sexo, col_kup, col_peso]):
            print(f"❌ Faltan columnas requeridas en {archivo_excel}")
            print(f"Columnas encontradas: {list(df.columns)}")
            print(f"Buscando: fecha (nacim/fecha/birth), sexo (sexo/genero/gender), nivel (kup/dan/nivel), peso (peso/weight/kg)")
            return None
        
        print(f"✅ Columnas identificadas:")
        print(f"  • Fecha: {col_fecha}")
        print(f"  • Sexo: {col_sexo}")
        print(f"  • Nivel: {col_kup}")
        print(f"  • Peso: {col_peso}")
        if col_abreviatura:
            print(f"  • Abreviación: {col_abreviatura}")
        else:
            print(f"  • Abreviación: No encontrada (opcional)")
        
        df['edad'] = df[col_fecha].apply(self.calcular_edad)
        df['sexo_normalizado'] = df[col_sexo].apply(self.normalizar_sexo)
        df['nivel_normalizado'] = df[col_kup].apply(self.normalizar_kup_dan)
        df['categoria_edad'] = df['edad'].apply(self.determinar_categoria_edad)
        df['categoria_peso'] = df.apply(lambda row: self.determinar_categoria_peso(row[col_peso], row['categoria_edad'], row['sexo_normalizado']), axis=1)
        
        # Agregar columna de abreviación si existe
        if col_abreviatura:
            df['abreviatura'] = df[col_abreviatura]
        else:
            df['abreviatura'] = ''
        
        return df
    def generar_nombre_categoria(self, categoria_edad, sexo, nivel, peso):
        if None in [categoria_edad, sexo, nivel, peso]:
            return None
        
        # Obtener nombre de la división de edad
        try:
            nombre_division = self.categorias['divisiones_edad'][categoria_edad]['nombre']
        except:
            nombre_division = categoria_edad.replace('_', ' ')
        
        return f"{nivel.title()} {nombre_division} {sexo} {peso}" 

class AgrupadorMultiple(AgrupadorTaekwondo):
    """Procesa múltiples archivos Excel y exporta categorías y solos."""
    def __init__(self, archivo_categorias="categorias_taekwondo.json"):
        super().__init__(archivo_categorias)
        self.archivos_procesados = []
        self.participantes_por_archivo = {}

    def procesar_multiples_archivos(self, archivos_excel, combinar=True):
        print(f"🔄 Procesando {len(archivos_excel)} archivos Excel...")
        todos_participantes = []
        participantes_por_archivo = {}
        archivos_exitosos = []
        archivos_fallidos = []
        for i, archivo in enumerate(archivos_excel, 1):
            try:
                print(f"\n📊 [{i}/{len(archivos_excel)}] Procesando: {Path(archivo).name}")
                df = self.procesar_participantes(archivo)
                if df is not None and len(df) > 0:
                    df['categoria_completa'] = df.apply(
                        lambda row: self.generar_nombre_categoria(
                            row['categoria_edad'],
                            row['sexo_normalizado'],
                            row['nivel_normalizado'],
                            row['categoria_peso']
                        ), axis=1
                    )
                    df['archivo_origen'] = Path(archivo).stem
                    participantes_por_archivo[Path(archivo).stem] = df
                    todos_participantes.append(df)
                    archivos_exitosos.append(archivo)
                    print(f"✅ {len(df)} participantes válidos encontrados")
                else:
                    print(f"❌ No se encontraron participantes válidos")
                    archivos_fallidos.append(archivo)
            except Exception as e:
                print(f"❌ Error procesando {Path(archivo).name}: {e}")
                archivos_fallidos.append(archivo)
        self.archivos_procesados = archivos_exitosos
        self.participantes_por_archivo = participantes_por_archivo
        if combinar and todos_participantes:
            df_combinado = pd.concat(todos_participantes, ignore_index=True)
            return df_combinado
        elif not combinar and participantes_por_archivo:
            return participantes_por_archivo
        else:
            print("❌ No se pudieron procesar participantes de ningún archivo")
            return None

    def identificar_solos(self, df):
        """Devuelve un DataFrame con los participantes que están solos en su categoría."""
        conteos = df['categoria_completa'].value_counts()
        categorias_solos = conteos[conteos == 1].index.tolist()
        df_solos = df[df['categoria_completa'].isin(categorias_solos)].copy()
        return df_solos

    def exportar_solos(self, df_solos, carpeta_salida):
        """Exporta los solos a un Excel en la carpeta de salida."""
        if not os.path.exists(carpeta_salida):
            os.makedirs(carpeta_salida)
        archivo = os.path.join(carpeta_salida, 'SOLOS.xlsx')
        df_solos.to_excel(archivo, index=False)
        print(f"✅ Excel de SOLOS exportado: {archivo}")
        return archivo

    def exportar_categorias_unico_excel(self, df, carpeta_salida):
        """Exporta todas las categorías a un solo Excel en la carpeta de salida."""
        if not os.path.exists(carpeta_salida):
            os.makedirs(carpeta_salida)
        archivo = os.path.join(carpeta_salida, 'CATEGORIAS.xlsx')
        df.to_excel(archivo, index=False)
        print(f"✅ Excel de categorías exportado: {archivo}")
        return archivo

# --- GENERACIÓN DE BRACKETS, IMÁGENES Y PDF ---
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from PIL import Image, ImageDraw, ImageFont
    import cv2
    import numpy as np
except ImportError:
    print("⚠️ Módulos adicionales requeridos para generar PDF y brackets:")
    print("pip install reportlab pillow opencv-python")
    print("Continuando sin funcionalidad de PDF y brackets...")

def detect_free_line_positions(image_path, line_length_thresh=20, hough_threshold=30, min_line_gap=5, merge_gap=10, branch_width=5, branch_height=5):
    """Detecta posiciones de líneas libres en la imagen del bracket."""
    try:
        pil_img = Image.open(image_path)
        gray = np.array(pil_img.convert('L'))
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        edges = cv2.Canny(binary, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=hough_threshold, minLineLength=line_length_thresh, maxLineGap=min_line_gap)
        centers = []
        if lines is not None:
            for x1, y1, x2, y2 in lines[:,0]:
                if abs(y1 - y2) > 10 or abs(x2 - x1) < line_length_thresh/2:
                    continue
                if x2 < x1:
                    x1, x2 = x2, x1
                centers.append(((x1+x2)//2, (y1+y2)//2))
        centers.sort(key=lambda c:c[1])
        merged = []
        for cx, cy in centers:
            if not any(abs(cy-mcy)<merge_gap and abs(cx-mcx)<merge_gap for mcx,mcy in merged):
                merged.append((cx, cy))
        return merged
    except Exception as e:
        print(f"Error en detección de líneas: {e}")
        return []

def load_font(font_type='regular', font_category='names'):
    """Load appropriate font based on type and category."""
    try:
        # Try to load system fonts first
        if font_category == 'category':
            if font_type == 'bold':
                try:
                    return ImageFont.truetype("arialbd.ttf", 72)
                except:
                    try:
                        return ImageFont.truetype("Arial-Bold.ttf", 72)
                    except:
                        return ImageFont.truetype("fonts/Anton-Regular.ttf", 72)
            else:
                return ImageFont.truetype("arial.ttf", 48)
        else:  # names
            if font_type == 'bold':
                try:
                    return ImageFont.truetype("arialbd.ttf", 36)
                except:
                    try:
                        return ImageFont.truetype("Arial-Bold.ttf", 36)
                    except:
                        return ImageFont.truetype("fonts/Anton-Regular.ttf", 36)
            else:
                try:
                    return ImageFont.truetype("arial.ttf", 32)
                except:
                    try:
                        return ImageFont.truetype("Arial.ttf", 32)
                    except:
                        return ImageFont.truetype("fonts/Roboto-VariableFont_wdth,wght.ttf", 32)
    except Exception as e:
        print(f"Error loading font: {e}")
        # Fallback to default font
        return ImageFont.load_default()

def detect_color_positions(image_path, area_thresh=20):
    """Detecta posiciones de círculos de colores en la imagen del bracket."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Cannot open image: {image_path}")
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Expanded color ranges
        color_ranges = [
            # Red ranges (expanded)
            (np.array([0,50,50]), np.array([10,255,255])),
            (np.array([160,50,50]), np.array([179,255,255])),
            # Blue range (expanded)
            (np.array([90,50,50]), np.array([130,255,255])),
            # Black range
            (np.array([0,0,0]), np.array([180,255,50])),
        ]
        
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for low, high in color_ranges:
            color_mask = cv2.inRange(hsv, low, high)
            mask = cv2.bitwise_or(mask, color_mask)
        
        # Improve circle detection
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        centers = []
        for cnt in contours:
            if cv2.contourArea(cnt) < area_thresh:
                continue
                
            # Check circularity
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * cv2.contourArea(cnt) / (perimeter * perimeter)
            if circularity < 0.5:
                continue
                
            M = cv2.moments(cnt)
            if M['m00'] == 0:
                continue
                
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            centers.append((cx, cy))
        
        # If no circles found, try to detect dots at the start of lines
        if not centers:
            # Find the leftmost point of each horizontal line
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                if cv2.contourArea(cnt) > 10:
                    leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
                    centers.append(leftmost)
        
        # Sort by y coordinate primarily, then x coordinate
        centers.sort(key=lambda c: (c[1], c[0]))
        
        return centers
    except Exception as e:
        print(f"Error en detect_color_positions: {e}")
        return []

def mark_positions(image_path, participants, output_path, category_name=None, font_path=None, font_size=None, margin=25, line_params=None, color_params=None):
    """
    Mark participant positions on a bracket template.
    """
    # Open image and convert to RGB
    pil_img = Image.open(image_path).convert('RGB')
    scale_factor = 4  # Quadruple the resolution for better quality
    high_res_img = pil_img.resize((pil_img.width * scale_factor, pil_img.height * scale_factor), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(high_res_img)
    
    # Get positions for participants
    free_lines = detect_free_line_positions(image_path, **(line_params or {}))
    circles = detect_color_positions(image_path, **(color_params or {}))
    
    # Handle case where we have more participants than detected positions
    count = min(len(participants), max(len(circles), len(free_lines)))
    participants = participants[:count]
    
    # If no circles detected, use the start of lines as positions
    if not circles and free_lines:
        circles = [(x-10, y) for x, y in free_lines]
    
    # Ensure we have enough circles
    while len(circles) < count:
        if free_lines:
            circles.append((free_lines[0][0]-10, free_lines[0][1]))
    
    circles = circles[:count]
    remaining_lines = free_lines.copy() if free_lines else []
    
    # If no lines detected but we have circles, create virtual lines
    if not remaining_lines and circles:
        for cx, cy in circles:
            remaining_lines.append((cx + 400, cy))  # Keep extended line length
    
    assignments = []
    for name, (cx, cy) in zip(participants, circles):
        best_idx, best_dist = None, float('inf')
        for i, (lx, ly) in enumerate(remaining_lines):
            d = (lx-cx)**2 + (ly-cy)**2
            if d < best_dist:
                best_dist, best_idx = d, i
        if best_idx is not None:
            assignments.append((name, (cx, cy), remaining_lines.pop(best_idx)))
        else:
            # If no line found, create a virtual line
            virtual_line = (cx + 400, cy)  # Keep extended line length
            assignments.append((name, (cx, cy), virtual_line))
    
    # Load fonts for category and names
    category_font = load_font('bold', 'category')
    names_font = load_font('regular', 'names')
    
    print("Loaded fonts:")
    print(f"Category font: {category_font}")
    print(f"Names font: {names_font}")
    
    # Add category name at the top if provided
    if category_name:
        # Calculate position for category name
        bbox = draw.textbbox((0,0), category_name, font=category_font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        
        # Position category name on the left with some margin
        tx = margin * 2 * scale_factor
        ty = margin * 1.5 * scale_factor
        
        # Draw a subtle underline
        underline_y = ty + th + margin * 0.75 * scale_factor
        draw.line([(tx, underline_y), (tx + tw + margin * scale_factor, underline_y)], 
                 fill=(0,0,0), width=1 * scale_factor)
        
        # Draw the category name in black
        draw.text((tx, ty), category_name, font=category_font, fill=(0,0,0))
    
    # Draw participant names
    for name, (cx, cy), (lx, ly) in assignments:
        # Scale coordinates for high resolution
        cx, cy = cx * scale_factor, cy * scale_factor
        lx, ly = lx * scale_factor, ly * scale_factor
        
        bbox = draw.textbbox((0,0), name, font=names_font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        
        # Improved positioning logic
        line_length = lx - cx
        
        # If line is too short or detection failed, use fixed positioning
        if line_length < 50:
            # Use fixed position relative to circle
            tx = cx + 60 * scale_factor  # Fixed offset from circle
            ty = cy - (th // 2)  # Center vertically on circle
        else:
            # Use line-based positioning with better logic
            # Position text at 70% along the line (closer to the line)
            text_position = 0.70
            tx = cx + (line_length * text_position) - (tw // 2)
            
            # Ensure text doesn't go too far left
            min_x = cx + 20 * scale_factor
            if tx < min_x:
                tx = min_x
            
            # Calculate vertical offset - position text closer to the line
            vertical_offset = th + 10 * scale_factor
            ty = ly - vertical_offset
        
        # Draw text in black
        draw.text((tx, ty), name, font=names_font, fill=(0,0,0))
    
    # Resize back to original size with high-quality downsampling
    final_img = high_res_img.resize(pil_img.size, Image.Resampling.LANCZOS)
    
    # Convert to RGB before saving
    final_img = final_img.convert('RGB')
    
    # Save with maximum quality
    final_img.save(output_path, format='PNG', optimize=False)

def generar_bracket_categoria(categoria, participantes, carpeta_salida, plantillas_path="bracket_templates"):
    """Genera un bracket para una categoría específica."""
    try:
        num_participantes = len(participantes)
        if num_participantes < 2:
            print(f"⚠️ Categoría {categoria} tiene menos de 2 participantes, saltando bracket")
            return None
        template_file = f"{plantillas_path}/{num_participantes}.png"
        if not os.path.exists(template_file):
            print(f"⚠️ No se encontró plantilla para {num_participantes} participantes")
            return None
        output_file = os.path.join(carpeta_salida, f"bracket_{categoria.replace(' ', '_')}.png")
        mark_positions(template_file, participantes, output_file, categoria)
        print(f"✅ Bracket generado: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error en generar_bracket_categoria: {e}")
        return None

def crear_pdf_brackets(imagenes_brackets, carpeta_salida):
    """Crea un PDF con todas las imágenes de brackets."""
    if not imagenes_brackets:
        print("⚠️ No hay imágenes de brackets para incluir en el PDF")
        return None
    try:
        pdf_path = os.path.join(carpeta_salida, "BRACKETS.pdf")
        c = canvas.Canvas(pdf_path, pagesize=A4)
        page_width, page_height = A4
        
        # Configuración para exactamente 2 brackets por página
        margin = 30
        vertical_gap = 5  # Minimal gap between brackets
        available_width = page_width - 2 * margin
        available_height = page_height - 2 * margin
        images_per_page = 2
        
        for page_start in range(0, len(imagenes_brackets), images_per_page):
            page_images = imagenes_brackets[page_start:page_start + images_per_page]
            num_images_on_page = len(page_images)
            
            # Calcular posiciones para esta página
            if num_images_on_page == 1:
                # Una imagen en la última página - usar toda la página
                positions = [(margin, margin, available_width, available_height)]
            else:  # 2 imágenes
                # Dos imágenes - apiladas verticalmente
                img_height = (available_height - vertical_gap) / 2
                positions = [
                    (margin, margin + img_height + vertical_gap, available_width, img_height),
                    (margin, margin, available_width, img_height)
                ]
            
            # Colocar imágenes en la página
            for i, imagen_path in enumerate(page_images):
                if i >= len(positions):
                    break
                    
                if os.path.exists(imagen_path):
                    x, y, max_width, max_height = positions[i]
                    
                    img = Image.open(imagen_path)
                    img_width, img_height = img.size
                    aspect_ratio = img_width / img_height
                    
                    # Ajustar imagen al espacio disponible
                    if aspect_ratio > max_width / max_height:
                        # Imagen más ancha - ajustar al ancho
                        new_width = max_width
                        new_height = new_width / aspect_ratio
                    else:
                        # Imagen más alta - ajustar a la altura
                        new_height = max_height
                        new_width = new_height * aspect_ratio
                    
                    # Centrar imagen en el espacio asignado
                    final_x = x + (max_width - new_width) / 2
                    final_y = y + (max_height - new_height) / 2
                    
                    c.drawImage(imagen_path, final_x, final_y, width=new_width, height=new_height)
            
            # Nueva página si hay más imágenes (excepto para la última página)
            if page_start + images_per_page < len(imagenes_brackets):
                c.showPage()
        
        c.save()
        total_pages = (len(imagenes_brackets) + images_per_page - 1) // images_per_page
        print(f"✅ PDF de brackets creado: {pdf_path}")
        print(f"📄 Total de páginas: {total_pages} ({len(imagenes_brackets)} brackets, 2 por página)")
        return pdf_path
    except Exception as e:
        print(f"Error creando PDF: {e}")
        return None

def generar_brackets_desde_excel(archivo_excel, carpeta_salida):
    """Genera brackets desde un archivo Excel de categorías."""
    try:
        df = pd.read_excel(archivo_excel)
        if 'categoria_completa' not in df.columns:
            print("❌ El archivo Excel no contiene la columna 'categoria_completa'")
            return None
        if not os.path.exists(carpeta_salida):
            os.makedirs(carpeta_salida)
        categorias = df['categoria_completa'].unique()
        imagenes_generadas = []
        for categoria in categorias:
            participantes_cat = df[df['categoria_completa'] == categoria]
            if len(participantes_cat) >= 2:
                # Crear lista de participantes con nombres completos y abreviación de academia
                participantes = []
                for _, row in participantes_cat.iterrows():
                    # Buscar columnas de nombre y apellido
                    nombre_col = None
                    apellido_col = None
                    abreviatura_col = None
                    for col in df.columns:
                        if 'nombre' in col.lower() and 'apellido' not in col.lower():
                            nombre_col = col
                        elif 'apellido' in col.lower():
                            apellido_col = col
                        elif 'abreviatura' in col.lower():
                            abreviatura_col = col
                    
                    if nombre_col and apellido_col:
                        nombre_completo = f"{row[nombre_col]} {row[apellido_col]}"
                    elif nombre_col:
                        nombre_completo = str(row[nombre_col])
                    else:
                        # Si no encuentra columnas de nombre, usar el índice
                        nombre_completo = f"Participante {row.name}"
                    
                    # Agregar abreviación de academia si existe
                    if abreviatura_col:
                        try:
                            abreviatura_valor = row[abreviatura_col]
                            if abreviatura_valor is not None and str(abreviatura_valor).strip():
                                abrev_str = str(abreviatura_valor).strip()
                                nombre_completo = f"{nombre_completo} ({abrev_str})"
                        except:
                            pass
                    
                    participantes.append(nombre_completo)
                
                imagen = generar_bracket_categoria(categoria, participantes, carpeta_salida)
                if imagen:
                    imagenes_generadas.append(imagen)
        if imagenes_generadas:
            pdf_path = crear_pdf_brackets(imagenes_generadas, carpeta_salida)
            return {'imagenes': imagenes_generadas, 'pdf': pdf_path}
        else:
            print("⚠️ No se generaron imágenes de brackets")
            return None
    except Exception as e:
        print(f"Error generando brackets desde Excel: {e}")
        return None

# --- FUNCIÓN DE PRUEBA DE ESTE BLOQUE ---
def prueba_excel_y_solos():
    """
    Prueba: procesa todos los Excel del directorio y exporta CATEGORIAS.xlsx y SOLOS.xlsx
    """
    print("\n=== PRUEBA DE EXPORTACIÓN DE EXCELS Y SOLOS ===\n")
    archivos_excel = list(Path('.').glob('*.xlsx'))
    if not archivos_excel:
        print("❌ No se encontraron archivos Excel en el directorio actual.")
        return
    agrupador = AgrupadorMultiple()
    df = agrupador.procesar_multiples_archivos([str(a) for a in archivos_excel], combinar=True)
    if df is not None and len(df) > 0:
        # Exportar Excel de categorías
        agrupador.exportar_categorias_unico_excel(df, 'resultados')
        # Identificar y exportar solos
        df_solos = agrupador.identificar_solos(df)
        agrupador.exportar_solos(df_solos, 'resultados')
        print(f"\nTotal de participantes: {len(df)}")
        print(f"Total de solos: {len(df_solos)}")
    else:
        print("❌ No se pudo procesar ningún participante.")

def prueba_brackets_y_pdf():
    """
    Prueba: genera brackets y PDF desde el Excel de categorías
    """
    print("\n=== PRUEBA DE GENERACIÓN DE BRACKETS Y PDF ===\n")
    excel_categorias = "resultados/CATEGORIAS.xlsx"
    if not os.path.exists(excel_categorias):
        print("❌ No se encontró el archivo de categorías. Ejecuta primero prueba_excel_y_solos().")
        return
    carpeta_brackets = "resultados/brackets"
    resultado = generar_brackets_desde_excel(excel_categorias, carpeta_brackets)
    if resultado:
        print(f"✅ Se generaron {len(resultado['imagenes'])} imágenes de brackets")
        if resultado['pdf']:
            print(f"✅ PDF de brackets creado: {resultado['pdf']}")
    else:
        print("❌ No se pudieron generar los brackets.")

# --- FUNCIÓN PRINCIPAL COMPLETA ---
def generar_torneo_completo():
    """
    Función principal que genera un torneo completo:
    - Procesa archivos Excel
    - Genera Excel de categorías
    - Genera Excel de solos
    - Genera brackets (imágenes y PDF)
    - Muestra resumen final
    """
    print("🥋 FILO 0.5-BETA - GENERADOR COMPLETO DE TORNEO 🥋")
    print("=" * 60)
    
    # Buscar archivos Excel
    archivos_excel = list(Path('.').glob('*.xlsx'))
    if not archivos_excel:
        print("❌ No se encontraron archivos Excel en el directorio actual.")
        print("💡 Coloca archivos Excel con inscripciones en este directorio.")
        return
    
    print(f"📁 Archivos Excel encontrados: {len(archivos_excel)}")
    for archivo in archivos_excel:
        print(f"  • {archivo.name}")
    
    try:
        # Crear agrupador
        agrupador = AgrupadorMultiple()
        
        # Procesar archivos
        print(f"\n🔄 Procesando {len(archivos_excel)} archivos...")
        df = agrupador.procesar_multiples_archivos([str(a) for a in archivos_excel], combinar=True)
        
        if df is not None and len(df) > 0:
            # Mostrar filas con categoria_completa None para depuración
            df_none = df[df['categoria_completa'].isnull()]
            if not df_none.empty:
                print("\n⚠️ Filas con categoria_completa = None (revisa estos datos en tu Excel):")
                print(df_none[['edad', 'sexo_normalizado', 'nivel_normalizado', 'categoria_edad', 'categoria_peso']])
            # Filtrar filas inválidas
            df = df[df['categoria_completa'].notnull()].copy()
            if len(df) == 0:
                print("❌ No quedan filas válidas para procesar después de filtrar None.")
                return

            # Validar categorías
            print("\n🔍 Validando categorías...")
            is_valid, invalid_categories = validate_categories(df)
            
            if not is_valid:
                print("❌ Categorías inválidas encontradas:")
                for cat in invalid_categories:
                    print(f"  • {cat}")
                print("\n💡 Verifica que las categorías coincidan con categorias_taekwondo.json")
                return
            
            print("✅ Todas las categorías son válidas!")
            
            # Crear carpeta de resultados
            carpeta_salida = "resultados"
            if not os.path.exists(carpeta_salida):
                os.makedirs(carpeta_salida)
            
            # 1. Exportar Excel de categorías
            print("\n📊 Exportando Excel de categorías...")
            excel_categorias = agrupador.exportar_categorias_unico_excel(df, carpeta_salida)
            
            # 2. Identificar y exportar solos
            print("\n👤 Identificando participantes solos...")
            df_solos = agrupador.identificar_solos(df)
            excel_solos = agrupador.exportar_solos(df_solos, carpeta_salida)
            
            # 3. Generar brackets
            print("\n🏆 Generando brackets...")
            carpeta_brackets = os.path.join(carpeta_salida, "brackets")
            resultado_brackets = generar_brackets_desde_excel(excel_categorias, carpeta_brackets)
            
            # 4. Generar resumen
            print("\n📋 Generando resumen...")
            generar_resumen_torneo(df, df_solos, resultado_brackets, carpeta_salida)
            
            # 5. Mostrar resultados finales
            print("\n" + "=" * 60)
            print("🎉 ¡TORNEO GENERADO EXITOSAMENTE! 🎉")
            print("=" * 60)
            print(f"📂 Carpeta de resultados: {Path(carpeta_salida).absolute()}")
            print(f"📊 Total participantes: {len(df)}")
            print(f"👤 Participantes solos: {len(df_solos)}")
            print(f"🏆 Categorías con brackets: {len(df) - len(df_solos)}")
            
            if resultado_brackets:
                print(f"🖼️  Imágenes de brackets: {len(resultado_brackets['imagenes'])}")
                if resultado_brackets['pdf']:
                    print(f"📄 PDF de brackets: {Path(resultado_brackets['pdf']).name}")
            
            print(f"\n📁 Archivos generados:")
            print(f"  • {Path(excel_categorias).name}")
            print(f"  • {Path(excel_solos).name}")
            if resultado_brackets and resultado_brackets['pdf']:
                print(f"  • {Path(resultado_brackets['pdf']).name}")
            print(f"  • resumen_torneo.txt")
            
        else:
            print("❌ No se pudieron procesar participantes de ningún archivo.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def generar_resumen_torneo(df, df_solos, resultado_brackets, carpeta_salida):
    """Genera un archivo de texto con el resumen del torneo."""
    try:
        archivo_resumen = os.path.join(carpeta_salida, "resumen_torneo.txt")
        
        with open(archivo_resumen, 'w', encoding='utf-8') as f:
            f.write("RESUMEN DEL TORNEO\n")
            f.write("=" * 50 + "\n\n")
            
            # Estadísticas generales
            f.write(f"Total de participantes: {len(df)}\n")
            f.write(f"Participantes solos: {len(df_solos)}\n")
            f.write(f"Categorías con brackets: {len(df) - len(df_solos)}\n\n")
            
            # Distribución por nivel
            f.write("DISTRIBUCIÓN POR NIVEL:\n")
            f.write("-" * 30 + "\n")
            nivel_counts = df['nivel_normalizado'].value_counts()
            for nivel, count in nivel_counts.items():
                f.write(f"{nivel}: {count} participantes\n")
            f.write("\n")
            
            # Distribución por sexo
            f.write("DISTRIBUCIÓN POR SEXO:\n")
            f.write("-" * 30 + "\n")
            sexo_counts = df['sexo_normalizado'].value_counts()
            for sexo, count in sexo_counts.items():
                f.write(f"{sexo}: {count} participantes\n")
            f.write("\n")
            
            # Categorías con más participantes
            f.write("CATEGORÍAS CON MÁS PARTICIPANTES:\n")
            f.write("-" * 40 + "\n")
            categoria_counts = df['categoria_completa'].value_counts().head(10)
            for categoria, count in categoria_counts.items():
                f.write(f"{categoria}: {count} participantes\n")
            f.write("\n")
            
            # Participantes solos
            f.write("PARTICIPANTES SOLOS:\n")
            f.write("-" * 30 + "\n")
            for _, row in df_solos.iterrows():
                f.write(f"• {row['categoria_completa']}\n")
            
            if resultado_brackets:
                f.write(f"\nBRACKETS GENERADOS: {len(resultado_brackets['imagenes'])}\n")
                f.write("-" * 30 + "\n")
                for imagen in resultado_brackets['imagenes']:
                    categoria = Path(imagen).stem.replace('bracket_', '').replace('_', ' ')
                    f.write(f"• {categoria}\n")
        
        print(f"✅ Resumen generado: {archivo_resumen}")
        return archivo_resumen
        
    except Exception as e:
        print(f"❌ Error generando resumen: {e}")
        return None

# --- MAIN ---
if __name__ == "__main__":
    generar_torneo_completo() 