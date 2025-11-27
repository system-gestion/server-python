"""
Modelo DetalleSesion: Registra las acciones realizadas durante una sesión.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Time
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class DetalleSesion(Base):
    """
    Tabla DetalleSesion
    
    Atributos:
        num_detalle (int): Número único del detalle [PK]
        tabla (str): Nombre de la tabla afectada
        accion (int): Tipo de acción (0 = consulta, 1 = edición, 2 = inserción, 3 = eliminación)
        hora (Time): Hora exacta de la acción
        cod_usuario (int): Código del usuario que realizó la acción [FK]
        num_sesion (int): Número de sesión asociada [FK]
    """
    __tablename__ = "detalle_sesion"

    num_detalle = Column(Integer, primary_key=True, index=True)
    tabla = Column(String(100), nullable=False)
    accion = Column(Integer, nullable=False)  # 0 = consulta, 1 = edición, 2 = inserción, 3 = eliminación
    hora = Column(Time, nullable=True, default=datetime.now().time)
    datos_json = Column(String, nullable=True)  # Snapshot para rollback (JSON string)
    cod_usuario = Column(Integer, ForeignKey("usuario.cod_usuario"), nullable=False)
    num_sesion = Column(Integer, ForeignKey("sesion_log.num_sesion"), nullable=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="detalles_sesion")
    sesion = relationship("SesionLog", back_populates="detalles")
