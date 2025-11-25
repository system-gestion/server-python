"""
Configuración de la conexión a la base de datos PostgreSQL con SQLAlchemy 2.0.
Maneja la creación del motor de base de datos y las sesiones.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings

# Crear el motor de base de datos con la URL de conexión
# echo=True muestra las consultas SQL en consola (útil en desarrollo)
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # Verifica la conexión antes de usar
    pool_size=10,  # Número de conexiones en el pool
    max_overflow=20  # Conexiones adicionales si el pool está lleno
)

# Crear la fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para los modelos declarativos
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Importar todos los modelos aquí para que sean registrados con Base
    from app.models import cliente, articulo, pedido, detalle_pedido, monitoreo, usuario, sesion_log, detalle_sesion
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas de base de datos creadas exitosamente")
