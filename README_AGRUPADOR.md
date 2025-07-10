# 🥋 Agrupador de Participantes de Taekwondo

Este sistema automatiza la agrupación de participantes de taekwondo según los criterios oficiales de categorías, peso, nivel, edad y sexo. **AHORA INCLUYE GENERACIÓN AUTOMÁTICA DE BRACKETS Y PDF!**

## 📋 Archivos Principales

- **`agrupador_taekwondo.py`** - Clase principal con toda la lógica de agrupación
- **`agrupador_multiple.py`** - Procesamiento múltiple y generación completa de torneos
- **`ejemplo_torneo_completo.py`** - Script de ejemplo para generar torneo completo
- **`brackets_real.py`** - Generador de brackets con imágenes
- **`categorias_taekwondo.json`** - Criterios oficiales de categorización
- **`requirements.txt`** - Dependencias del proyecto

## 🚀 Uso Rápido

### ⭐ NUEVO: Generación Completa de Torneo
```bash
# Generar Excel único + brackets + PDF de un archivo
python agrupador_multiple.py "archivo.xlsx" --completo -o "mi_torneo"

# Generar desde múltiples archivos
python agrupador_multiple.py *.xlsx --completo -o "torneo_completo"

# Generar desde carpeta completa
python agrupador_multiple.py --carpeta "mi_carpeta" --completo -o "torneo_final"
```

### Opciones Tradicionales
```bash
# Script simple
python ejemplo_torneo_completo.py

# Procesamiento individual
python agrupador_taekwondo.py "archivo.xlsx" -o "carpeta_salida"

# Procesamiento múltiple combinado
python agrupador_multiple.py *.xlsx -o "carpeta_salida"

# Procesamiento múltiple separado
python agrupador_multiple.py *.xlsx --separado -o "carpeta_salida"
```

## 🎯 Funcionalidades Nuevas

### 📊 Excel Único con Múltiples Hojas
- Todas las categorías en un solo archivo Excel
- Cada categoría en una hoja separada
- Compatible con el generador de brackets
- Archivo `SOLOS.xlsx` separado para participantes sin oponentes

### 🖼️ Generación Automática de Brackets
- Genera automáticamente todas las imágenes de brackets
- Usa las plantillas existentes del sistema
- Nombres de participantes agregados automáticamente
- Categorías organizadas por carpetas

### 📄 PDF con Todas las Llaves
- Un solo PDF con todos los brackets del torneo
- Calidad optimizada para impresión
- Cada bracket en una página separada
- Formato A4 estándar

## 📊 Formato del Archivo Excel

Tu archivo Excel debe contener las siguientes columnas (los nombres pueden variar):

| Columna Requerida | Nombres Aceptados | Ejemplo |
|-------------------|-------------------|---------|
| **Nombres** | NOMBRES, NAME, Nombre | Juan Carlos |
| **Apellidos** | APELLIDOS, SURNAME, Apellido | Pérez García |
| **Fecha de Nacimiento** | Fecha de Nacimiento, BIRTH DATE | 15/03/2010 |
| **Peso** | PESO, WEIGHT | 45.5 |
| **Nivel** | KUP, DAN, GRADO | 5to KUP, 1er DAN |
| **Sexo** | SEXO, GÉNERO, GENDER | M, F, Masculino, Femenino |

## 🎯 Criterios de Agrupación

### Categorías de Edad
- **PRE_INFANTIL**: 4-5 años
- **INFANTIL_A**: 6-7 años  
- **INFANTIL_B**: 8-9 años
- **INFANTIL_C**: 10-11 años
- **CADETE**: 12-14 años
- **JUVENIL**: 15-17 años
- **MAYORES**: 18+ años

### Niveles (basado en KUP/DAN)
- **Festival**: KUP 10, 9, 8, 7
- **Noveles**: KUP 6, 5, 4, 3
- **Avanzados**: KUP 2, KUP 1 y todos los DAN

### Pesos
Cada categoría de edad tiene rangos específicos de peso por sexo (ver `categorias_taekwondo.json`)

## 📁 Archivos de Salida

### Modo Completo (--completo)
```
torneo_completo/
├── TODAS_LAS_CATEGORIAS.xlsx    # Excel único con todas las categorías
├── SOLOS.xlsx                   # Participantes sin oponentes
├── brackets/                    # Carpeta con imágenes de brackets
│   ├── categoria1_bracket.jpg
│   ├── categoria2_bracket.jpg
│   └── ...
├── TODOS_LOS_BRACKETS.pdf      # PDF con todos los brackets
├── resumen_archivos_origen.xlsx
└── reporte_procesamiento_multiple.txt
```

### Modo Tradicional
Los participantes se agrupan en archivos Excel separados con el formato:
```
NIVEL_CATEGORIA_EDAD_SEXO_PESO.xlsx
```

**Ejemplos:**
- `Festival_INFANTIL_A_MASCULINO_-25KG.xlsx`
- `Noveles_CADETE_FEMENINO_-41KG.xlsx`
- `Avanzados_MAYORES_MASCULINO_-68KG.xlsx`

## 🛠️ Instalación de Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- `pandas` - Procesamiento de datos
- `openpyxl` - Manejo de archivos Excel
- `reportlab` - Generación de PDFs
- `pillow` - Procesamiento de imágenes
- `opencv-python` - Detección de elementos en brackets
- `flask` - Servidor web para generador de brackets

## 📖 Ejemplos de Uso

### Ejemplo 1: Torneo Simple
```python
from agrupador_multiple import AgrupadorMultiple

agrupador = AgrupadorMultiple()
df = agrupador.procesar_participantes("participantes.xlsx")
resultados = agrupador.generar_todo_completo(df, "mi_torneo")
```

### Ejemplo 2: Múltiples Archivos
```python
archivos = ["archivo1.xlsx", "archivo2.xlsx", "archivo3.xlsx"]
agrupador = AgrupadorMultiple()
df_combinado = agrupador.procesar_multiples_archivos(archivos)
resultados = agrupador.generar_todo_completo(df_combinado, "torneo_grande")
```

### Ejemplo 3: Línea de Comandos
```bash
# Generar todo desde múltiples archivos
python agrupador_multiple.py participantes_*.xlsx --completo -o "torneo_2024"

# Solo Excel único (sin brackets ni PDF)
python agrupador_multiple.py participantes_*.xlsx -o "solo_excel"
```

## 🎮 Servidor Web para Brackets Individuales

Si necesitas generar brackets individuales, usa el servidor web:

```bash
python brackets_real.py
```

Luego ve a `http://localhost:5000` y sube un archivo Excel individual.

## 🐛 Solución de Problemas

### Error: "No se pudo importar brackets_real.py"
- Asegúrate de que `brackets_real.py` esté en el mismo directorio
- Verifica que las dependencias de Flask y OpenCV estén instaladas

### Error: "No se pueden crear PDFs"
```bash
pip install reportlab pillow
```

### Brackets no se generan
- Verifica que existan las plantillas en `bracket_templates/`
- Asegúrate de que el número de participantes tenga una plantilla correspondiente

### Texto muy pequeño en brackets
- Modifica `font_size` en `brackets_real.py` (línea ~123)
- Valores recomendados: 50-200 según el tamaño de la plantilla

## 📞 Soporte

Si encuentras problemas:
1. Verifica que todas las dependencias estén instaladas
2. Revisa que tus archivos Excel tengan el formato correcto
3. Asegúrate de que las plantillas de brackets existan
4. Revisa los mensajes de error en la consola

## 🏆 Flujo Completo Recomendado

1. **Preparar datos**: Organiza tus archivos Excel con participantes
2. **Ejecutar agrupador**: `python agrupador_multiple.py *.xlsx --completo -o "torneo"`
3. **Revisar resultados**: Verifica el Excel único y el archivo de solos
4. **Imprimir brackets**: Usa el PDF generado para imprimir todas las llaves
5. **Gestionar torneo**: Usa los brackets impresos para organizar la competencia

¡El sistema ahora automatiza todo el proceso desde la inscripción hasta los brackets listos para imprimir! 🥋✨ 