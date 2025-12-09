"""
Modelo DetallePedido: Representa los artículos incluidos en cada pedido.
"""

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class DetallePedido(Base):
    """
    Tabla DetallePedido
    
    Atributos:
        num_pedido (int): Número del pedido [FK, PK]
        cod_articulo (int): Código del artículo [FK, PK]
        cantidad (int): Cantidad de artículos
        subtotal (float): Subtotal de la línea (cantidad * precio)
        estado (int): Estado del detalle (0 = quitado, 1 = activo)
    """
    __tablename__ = "detalle_pedido"

    num_pedido = Column(Integer, ForeignKey("pedido.num_pedido", ondelete="CASCADE"), primary_key=True)
    cod_articulo = Column(Integer, ForeignKey("articulo.cod_articulo", ondelete="CASCADE"), primary_key=True)
    cantidad = Column(Integer, nullable=False, default=1)
    subtotal = Column(Float, nullable=False, default=0.0)
    estado = Column(Integer, nullable=False, default=1)  # 0 = quitado, 1 = activo

    # Relaciones
    pedido = relationship("Pedido", back_populates="detalles")
    articulo = relationship("Articulo", back_populates="detalles")
