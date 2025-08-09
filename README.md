# 🥋 FILO 0.5 - Generador de Torneos de Taekwondo

**Logo:** El archivo del logo se encuentra en la raíz del proyecto como `mexxus arena 2.png`. Para producción, se recomienda moverlo a una carpeta `static/`.

Sistema web para la gestión y generación automática de torneos de Taekwondo.

## 🚀 Características

- **Procesamiento automático** de archivos Excel con listas de participantes
- **Generación de brackets** automática para diferentes categorías
- **Identificación de participantes solos** (sin oponentes)
- **Exportación de resultados** en múltiples formatos (Excel, PDF, imágenes)
- **Interfaz web moderna** y fácil de usar
- **Soporte para múltiples archivos** de entrada

## 🛠️ Tecnologías

- **Backend**: Python + Flask
- **Frontend**: HTML5 + CSS3 + JavaScript
- **Procesamiento**: Pandas, OpenCV, Pillow
- **Generación de documentos**: ReportLab

## 📋 Requisitos

- Python 3.8+
- Dependencias listadas en `requirements_web.txt`

## 🚀 Instalación Local

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/filo-0.5.git
cd filo-0.5
```

2. **Crear entorno virtual:**
```bash
python -m venv .venv
```

3. **Activar entorno virtual:**
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. **Instalar dependencias:**
```bash
pip install -r requirements_web.txt
```

5. **Ejecutar la aplicación:**
```bash
python app.py
```

6. **Abrir en el navegador:**
```
http://localhost:5000
```

## 📁 Estructura del Proyecto

```
filo_0.5/
├── app.py                 # Aplicación Flask principal
├── filo_0_5.py           # Lógica de procesamiento
├── templates/
│   └── index.html        # Interfaz web
├── uploads/              # Archivos subidos temporalmente
├── results/              # Resultados generados
├── bracket_templates/    # Plantillas de brackets
└── requirements_web.txt  # Dependencias
```

## 🎯 Uso

1. **Subir archivos Excel** con listas de participantes
2. **Procesar automáticamente** las categorías
3. **Generar brackets** para cada categoría
4. **Descargar resultados** en formato ZIP

## 🌐 Despliegue

### Render.com (Recomendado)
1. Conecta tu repositorio a Render.com
2. Crea un nuevo Web Service
3. Render detectará automáticamente la configuración

### Railway.app
1. Conecta tu repositorio a Railway.app
2. Railway detectará automáticamente la configuración

## 📝 Formato de Archivos de Entrada

Los archivos Excel deben contener columnas con:
- Nombre del participante
- Categoría
- Peso
- Edad
- Género

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

Desarrollado para la gestión de torneos de Taekwondo.

---

**¡Gracias por usar FILO 0.5! 🥋** 