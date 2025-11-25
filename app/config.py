"""
Archivo de configuración de la aplicación.
Lee las variables de entorno desde el archivo .env usando python-dotenv.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()


class Settings:
    """Clase que contiene todas las configuraciones de la aplicación"""
    
    # Configuración de la base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/db")
    
    # Configuración del servidor
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Configuración adicional
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key")
    
    # Información del proyecto
    PROJECT_NAME: str = "FastAPI REST API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API REST completa con FastAPI y PostgreSQL"


# Instancia global de configuración
settings = Settings()
