"""
Schemas Pydantic para Pedido y DetallePedido
"""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List


class DetallePedidoBase(BaseModel):
    cod_articulo: int
    cantidad: int = Field(..., ge=1)
    subtotal: float = Field(..., ge=0)
    estado: int = Field(default=1, ge=0, le=1)


class DetallePedidoCreate(DetallePedidoBase):
    pass


class DetallePedidoResponse(DetallePedidoBase):
    num_pedido: int
    nombre_articulo: Optional[str] = None
    pvp: Optional[float] = None

    class Config:
        from_attributes = True


class PedidoBase(BaseModel):
    """
    Schema base para Pedido
    
    estado: 1=Pendiente, 2=Completado, 3=Cancelado
    """
    fecha: date = Field(default_factory=date.today)
    importe: float = Field(..., ge=0)
    cod_cliente: str
    cod_vendedor: int
    estado: int = Field(default=1, ge=1, le=3)


class PedidoCreate(PedidoBase):
    detalles: Optional[List[DetallePedidoCreate]] = []


class PedidoUpdate(BaseModel):
    """
    Schema para actualizar Pedido
    
    estado: 1=Pendiente, 2=Completado, 3=Cancelado
    """
    fecha: Optional[date] = None
    importe: Optional[float] = Field(None, ge=0)
    cod_cliente: Optional[str] = None
    cod_vendedor: Optional[int] = None
    estado: Optional[int] = Field(None, ge=1, le=3)


class PedidoResponse(PedidoBase):
    num_pedido: int
    nombre_cliente: Optional[str] = None
    nombre_vendedor: Optional[str] = None
    detalles: List[DetallePedidoResponse] = []

    class Config:
        from_attributes = True


class PedidoEstadistica(BaseModel):
    total_pedidos: int
    importe_total: float
    promedio: float
    pendientes: int
    completados: int
    cancelados: int
