"""
Schemas Pydantic para Cliente
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class ClienteBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre completo del cliente")
    direccion: Optional[str] = Field(None, max_length=300)
    telefono: Optional[str] = Field(None, max_length=20)


class ClienteCreate(ClienteBase):
    cod_cliente: str = Field(..., max_length=50)
    # Datos de usuario
    correo: EmailStr = Field(..., description="Correo electrónico (será el usuario)")
    celular: Optional[str] = Field(None, max_length=20)
    password: str = Field(..., min_length=6, description="Contraseña del usuario")


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    direccion: Optional[str] = Field(None, max_length=300)
    telefono: Optional[str] = Field(None, max_length=20)
    # Datos de usuario
    correo: Optional[EmailStr] = None
    celular: Optional[str] = Field(None, max_length=20)
    password: Optional[str] = Field(None, min_length=6, description="Nueva contraseña (opcional)")


class ClienteResponse(ClienteBase):
    cod_cliente: str
    cod_usuario: Optional[int] = None
    # Datos de usuario
    correo: Optional[str] = None
    celular: Optional[str] = None
    estado: Optional[int] = None

    class Config:
        from_attributes = True
