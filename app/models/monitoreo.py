"""
Modelo Monitoreo: Registra el estado del VPS en diferentes momentos.
"""

from sqlalchemy import Column, Integer, Date
from datetime import date

from app.database import Base


class Monitoreo(Base):
    """
    Tabla Monitoreo
    
    Atributos:
        num_registro (int): Número único de registro [PK]
        fecha (date): Fecha del registro
        estado_vps (int): Estado del VPS (0 = inactivo, 1 = activo)
    """
    __tablename__ = "monitoreo"

    num_registro = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, default=date.today)
    estado_vps = Column(Integer, nullable=False, default=1)  # 0 = inactivo, 1 = activo
