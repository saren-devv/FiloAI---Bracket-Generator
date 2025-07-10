# 🥋 INSTRUCCIONES DE USO - GENERADOR COMPLETO DE TORNEO

## ✨ NUEVA FUNCIONALIDAD AGREGADA

Tu código ahora puede generar automáticamente:
1. **Excel único** con todas las categorías en hojas separadas
2. **Imágenes de brackets** para todas las categorías automáticamente  
3. **PDF con todas las llaves** listo para imprimir
4. **Archivo de solos** separado para participantes sin oponentes

## 🚀 CÓMO USAR

### Opción 1: Comando Simple (RECOMENDADO)
```bash
# Para un archivo:
python agrupador_multiple.py "mi_archivo.xlsx" --completo -o "mi_torneo"

# Para múltiples archivos:
python agrupador_multiple.py *.xlsx --completo -o "torneo_completo"

# Para una carpeta completa:
python agrupador_multiple.py --carpeta "mi_carpeta" --completo -o "torneo_final"
```

### Opción 2: Script de Ejemplo
```bash
python ejemplo_torneo_completo.py
```

## 📋 LO QUE SE GENERA

Después de ejecutar el comando, tendrás una carpeta con:

```
mi_torneo/
├── TODAS_LAS_CATEGORIAS.xlsx     # Excel único - USAR ESTO PARA GENERAR BRACKETS
├── SOLOS.xlsx                    # Participantes sin oponentes
├── brackets/                     # Carpeta con todas las imágenes
│   ├── categoria1_bracket.jpg
│   ├── categoria2_bracket.jpg
│   └── ...
├── TODOS_LOS_BRACKETS.pdf       # PDF para imprimir - ¡LISTO PARA USAR!
├── resumen_archivos_origen.xlsx # Estadísticas
└── reporte_procesamiento_multiple.txt
```

## 🎯 FLUJO DE TRABAJO COMPLETO

1. **Organiza tus archivos Excel** con los participantes
2. **Ejecuta el comando** `--completo`
3. **Revisa el archivo `TODAS_LAS_CATEGORIAS.xlsx`** para verificar las categorías
4. **Imprime el PDF `TODOS_LOS_BRACKETS.pdf`** - ¡ya tienes todas las llaves!
5. **Usa `SOLOS.xlsx`** para participantes que no tienen oponentes

## 📊 DIFERENCIAS CON EL SISTEMA ANTERIOR

### ANTES:
- ❌ Un Excel por cada categoría (muchos archivos)
- ❌ Tenías que generar brackets uno por uno
- ❌ No había PDF automático

### AHORA:
- ✅ **UN SOLO EXCEL** con todas las categorías
- ✅ **BRACKETS AUTOMÁTICOS** para todas las categorías
- ✅ **PDF COMPLETO** listo para imprimir
- ✅ Todo en un solo comando

## 🛠️ INSTALACIÓN DE DEPENDENCIAS NUEVAS

Si es la primera vez que usas la nueva función:
```bash
pip install reportlab pillow
```

## 💡 CONSEJOS

1. **Para torneos grandes**: Usa el flag `--completo` siempre
2. **Para revisar categorías**: Abre `TODAS_LAS_CATEGORIAS.xlsx` antes de imprimir
3. **Para imprimir**: Usa directamente `TODOS_LOS_BRACKETS.pdf`
4. **Para participantes solos**: Revisa `SOLOS.xlsx` y decide qué hacer con ellos

## 🎮 GENERADOR WEB (Uso Individual)

Si necesitas generar brackets individuales, aún puedes usar:
```bash
python brackets_real.py
```
Luego ve a `http://localhost:5000`

## 🏆 EJEMPLO PRÁCTICO

```bash
# Tienes varios archivos Excel de inscripciones
python agrupador_multiple.py *.xlsx --completo -o "torneo_taekwondo_2024"

# Resultado: Una carpeta con TODO listo:
# - Excel único para revisar
# - PDF completo para imprimir
# - Brackets individuales si los necesitas
```

## ❓ SOLUCIÓN DE PROBLEMAS

**Error: "No se pudo importar brackets_real.py"**
- Asegúrate de que todos los archivos estén en la misma carpeta

**Error: "No se pueden crear PDFs"**
```bash
pip install reportlab pillow
```

**No se generan brackets:**
- Verifica que existan plantillas en `bracket_templates/`
- Solo se generan brackets para categorías con 2+ participantes

**Texto muy pequeño:**
- El tamaño se ajustó a 200px por defecto (mucho más grande que antes)

## 🎉 ¡DISFRUTA TU NUEVO SISTEMA AUTOMATIZADO!

Ya no necesitas hacer nada manual. Un comando y tienes todo el torneo listo para organizar e imprimir. 🥋✨ 