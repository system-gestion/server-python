"""
Schemas Pydantic para Articulo (Ofertas)
"""
from pydantic import BaseModel, Field
from typing import Optional


class ArticuloBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    pvp: float = Field(..., ge=0)
    stock: int = Field(..., ge=0)


class ArticuloCreate(ArticuloBase):
    cod_articulo: int


class ArticuloUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    pvp: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)


class ArticuloResponse(ArticuloBase):
    cod_articulo: int

    class Config:
        from_attributes = True


class OfertaResponse(ArticuloResponse):
    en_oferta: bool = True
    descuento: Optional[float] = None
    precio_oferta: Optional[float] = None
