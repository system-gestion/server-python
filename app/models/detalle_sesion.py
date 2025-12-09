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
        accion (int): Tipo de acción 
            0 = consulta
            1 = edición
            2 = inserción
            3 = eliminación
            4 = rollback
        hora (Time): Hora exacta de la acción
        datos_json (str): Snapshot para rollback (JSON string)
        rollback_realizado (int): Indica si se hizo rollback (0 = no, 1 = sí)
        cod_usuario (int): Código del usuario que realizó la acción [FK]
        num_sesion (int): Número de sesión asociada [FK]
    """
    __tablename__ = "detalle_sesion"

    num_detalle = Column(Integer, primary_key=True, index=True)
    tabla = Column(String(100), nullable=False)
    accion = Column(Integer, nullable=False)  # 0 = consulta, 1 = edición, 2 = inserción, 3 = eliminación, 4 = rollback
    hora = Column(Time, nullable=True, default=datetime.now().time)
    datos_json = Column(String, nullable=True)  # Snapshot para rollback (JSON string)
    rollback_realizado = Column(Integer, nullable=False, default=0)  # 0 = no, 1 = sí
    cod_usuario = Column(Integer, ForeignKey("usuario.cod_usuario", ondelete="CASCADE"), nullable=False)
    num_sesion = Column(Integer, ForeignKey("sesion_log.num_sesion", ondelete="CASCADE"), nullable=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="detalles_sesion")
    sesion = relationship("SesionLog", back_populates="detalles")
