"""
Modelo Cliente: Representa a los clientes de la empresa.
"""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.database import Base


class Cliente(Base):
    """
    Tabla Cliente
    
    Atributos:
        cod_cliente (str): Código único del cliente [PK]
        nombre (str): Nombre del cliente
        direccion (str): Dirección del cliente
        telefono (str): Teléfono del cliente
    """
    __tablename__ = "cliente"

    from sqlalchemy import ForeignKey, Integer

    cod_cliente = Column(String(50), primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    direccion = Column(String(300))
    telefono = Column(String(20))
    
    # Relación con Usuario
    cod_usuario = Column(Integer, ForeignKey("usuario.cod_usuario"), nullable=True, unique=True)
    usuario = relationship("Usuario", back_populates="cliente")

    # Relación con pedidos
    pedidos = relationship("Pedido", back_populates="cliente")
