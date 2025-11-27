"""
Schemas Pydantic para Articulo (Ofertas)
"""
from pydantic import BaseModel, Field
from typing import Optional


class ArticuloBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    pvp: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    tipo_descuento: Optional[int] = Field(0, description="0=Sin oferta, 1=Fijo, 2=Porcentual")
    valor_descuento: Optional[float] = Field(0.0, ge=0)


class ArticuloCreate(ArticuloBase):
    cod_articulo: Optional[int] = None


class ArticuloUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    pvp: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    tipo_descuento: Optional[int] = None
    valor_descuento: Optional[float] = None


class ArticuloResponse(ArticuloBase):
    cod_articulo: int

    class Config:
        from_attributes = True
