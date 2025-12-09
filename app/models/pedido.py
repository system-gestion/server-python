"""
Modelo Pedido: Representa los pedidos realizados por los clientes.
"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date

from app.database import Base


class Pedido(Base):
    """
    Tabla Pedido
    
    Atributos:
        num_pedido (int): Número único del pedido [PK]
        fecha (date): Fecha del pedido
        importe (float): Importe total del pedido
        cod_cliente (str): Código del cliente que realizó el pedido [FK]
        cod_vendedor (int): Código del vendedor que generó el pedido [FK]
        estado (int): Estado del pedido
            1 = Pendiente (pending)
            2 = Completado (completed)
            3 = Cancelado (cancelled)
    """
    __tablename__ = "pedido"

    num_pedido = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, default=date.today)
    importe = Column(Float, nullable=False, default=0.0)
    cod_cliente = Column(String(50), ForeignKey("cliente.cod_cliente"), nullable=False)
    cod_vendedor = Column(Integer, ForeignKey("usuario.cod_usuario"), nullable=False)
    estado = Column(Integer, nullable=False, default=1)  # 1=pending, 2=completed, 3=cancelled

    # Relaciones
    cliente = relationship("Cliente", back_populates="pedidos")
    vendedor = relationship("Usuario", foreign_keys=[cod_vendedor])
    detalles = relationship("DetallePedido", back_populates="pedido", cascade="all, delete-orphan")
