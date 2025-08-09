import os

class Config:
    """Configuración base para la aplicación"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    UPLOAD_FOLDER = 'uploads'
    RESULTS_FOLDER = 'results'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    HOST = 'localhost'
    PORT = 5000

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))

# Configuración por defecto basada en variable de entorno
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtiene la configuración basada en la variable de entorno FLASK_ENV"""
    env = os.environ.get('FLASK_ENV', 'default')
    return config[env]
