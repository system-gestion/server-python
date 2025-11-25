"""
Schemas para Comisiones de Vendedores
"""
from pydantic import BaseModel
from datetime import date
from typing import Optional


class ComisionResponse(BaseModel):
    cod_usuario: int
    nombre_vendedor: str
    total_ventas: float
    cantidad_pedidos: int
    porcentaje_comision: float = 5.0  # 5% por defecto
    comision_total: float
    periodo_inicio: date
    periodo_fin: date


class ComisionDetalle(BaseModel):
    num_pedido: int
    fecha: date
    cod_cliente: str
    nombre_cliente: Optional[str] = None
    importe: float
    comision: float
