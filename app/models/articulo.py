"""
Modelo Articulo: Representa los artículos/productos disponibles.
"""

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.database import Base


class Articulo(Base):
    """
    Tabla Articulo
    
    Atributos:
        cod_articulo (int): Código único del artículo [PK]
        nombre (str): Nombre del artículo
        pvp (float): Precio de venta al público
        stock (int): Cantidad disponible en inventario
        tipo_descuento (int): Tipo de descuento (0=Sin oferta, 1=Fijo, 2=Porcentual)
        valor_descuento (float): Valor del descuento
    """
    __tablename__ = "articulo"

    cod_articulo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    pvp = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    
    # Campos de oferta
    tipo_descuento = Column(Integer, nullable=True, default=0)  # 0=Sin oferta, 1=Fijo, 2=Porcentual
    valor_descuento = Column(Float, nullable=True, default=0.0)

    # Relación con detalle_pedido
    detalles = relationship("DetallePedido", back_populates="articulo")
