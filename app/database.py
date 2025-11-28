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
    """Verifica la conexión a la base de datos"""
    try:
        # Intentar una conexión simple
        with engine.connect() as connection:
            from sqlalchemy import text
            connection.execute(text("SELECT 1"))
        print("✅ Conexión a base de datos exitosa")
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        raise e
