from pydantic import BaseModel, Field
from typing import Optional
from .articulo import ArticuloResponse

class OfertaResponse(ArticuloResponse):
    pass

class OfertaCreate(BaseModel):
    cod_articulo: int
    tipo_descuento: int = Field(..., description="1=Fijo, 2=Porcentual")
    valor_descuento: float = Field(..., gt=0)

class OfertaUpdate(BaseModel):
    tipo_descuento: Optional[int] = Field(None, description="1=Fijo, 2=Porcentual")
    valor_descuento: Optional[float] = Field(None, gt=0)
