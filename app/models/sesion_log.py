"""
Modelo SesionLog: Registra las sesiones de usuarios en el sistema.
"""

from sqlalchemy import Column, Integer, Date
from sqlalchemy.orm import relationship
from datetime import date

from app.database import Base


class SesionLog(Base):
    """
    Tabla SesionLog
    
    Atributos:
        num_sesion (int): Número único de sesión [PK]
        fecha_inicio (date): Fecha y hora de inicio de sesión
        fecha_fin (date): Fecha y hora de fin de sesión
        estado (int): Estado de la sesión (0 = inactivo, 1 = activo)
    """
    __tablename__ = "sesion_log"

    num_sesion = Column(Integer, primary_key=True, index=True)
    fecha_inicio = Column(Date, nullable=False, default=date.today)
    fecha_fin = Column(Date, nullable=True)
    estado = Column(Integer, nullable=False, default=1)  # 0 = inactivo, 1 = activo

    # Relación con detalle_sesion
    detalles = relationship("DetalleSesion", back_populates="sesion", cascade="all, delete")
