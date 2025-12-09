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
        direccion (str): Dirección del cliente
        cod_usuario (int): Código del usuario asociado [FK]
    
    Nota: nombre, apellidos y telefono se obtienen del Usuario relacionado
    """
    __tablename__ = "cliente"

    from sqlalchemy import ForeignKey, Integer

    cod_cliente = Column(String(50), primary_key=True, index=True)
    direccion = Column(String(300))
    
    # Relación con Usuario
    cod_usuario = Column(Integer, ForeignKey("usuario.cod_usuario", ondelete="CASCADE"), nullable=False, unique=True)
    usuario = relationship("Usuario", back_populates="cliente")

    # Relación con pedidos
    pedidos = relationship("Pedido", back_populates="cliente", cascade="all, delete")
