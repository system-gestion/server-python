"""
Schemas Pydantic para Cliente
"""
from pydantic import BaseModel, Field
from typing import Optional


class ClienteBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    direccion: Optional[str] = Field(None, max_length=300)
    telefono: Optional[str] = Field(None, max_length=20)


class ClienteCreate(ClienteBase):
    cod_cliente: str = Field(..., max_length=50)


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    direccion: Optional[str] = Field(None, max_length=300)
    telefono: Optional[str] = Field(None, max_length=20)


class ClienteResponse(ClienteBase):
    cod_cliente: str

    class Config:
        from_attributes = True
