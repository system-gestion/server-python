"""
Modelo Usuario: Representa los usuarios del sistema.
"""

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from datetime import date

from app.database import Base


class Usuario(Base):
    """
    Tabla Usuario
    
    Atributos:
        cod_usuario (int): Código único del usuario [PK]
        apellidos (str): Apellidos del usuario
        nombres (str): Nombres del usuario
        nivel (int): Nivel de acceso (1 = supervisor, 2 = vendedor, 3 = cliente)
        correo (str): Correo electrónico
        celular (str): Número de celular
        fecha_ingreso (date): Fecha de ingreso al sistema
        estado (int): Estado del usuario (0 = de baja, 1 = activo)
        fecha_baja (date): Fecha de baja (null si está activo)
        password (str): Contraseña del usuario (debe estar hasheada)
        email_verificado (int): Estado de verificación del email (0 = no verificado, 1 = verificado)
    """
    __tablename__ = "usuario"

    cod_usuario = Column(Integer, primary_key=True, index=True)
    apellidos = Column(String(100), nullable=False)
    nombres = Column(String(100), nullable=False)
    nivel = Column(Integer, nullable=False)  # 1 = supervisor, 2 = vendedor, 3 = cliente
    correo = Column(String(100), unique=True, nullable=False, index=True)
    celular = Column(String(20))
    fecha_ingreso = Column(Date, nullable=False, default=date.today)
    estado = Column(Integer, nullable=False, default=1)  # 0 = de baja, 1 = activo
    fecha_baja = Column(Date, nullable=True)
    password = Column(String(255), nullable=False)
    email_verificado = Column(Integer, nullable=False, default=0)  # 0 = no verificado, 1 = verificado

    # Relación con detalle_sesion
    detalles_sesion = relationship("DetalleSesion", back_populates="usuario", cascade="all, delete")
    
    # Relación con cliente (Uno a Uno)
    cliente = relationship("Cliente", back_populates="usuario", uselist=False, cascade="all, delete")

    @property
    def cod_cliente(self):
        return self.cliente.cod_cliente if self.cliente else None
