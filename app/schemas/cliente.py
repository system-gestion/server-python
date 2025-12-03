"""
Schemas Pydantic para Cliente
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class ClienteBase(BaseModel):
    direccion: Optional[str] = Field(None, max_length=300)


class ClienteCreate(ClienteBase):
    cod_cliente: str = Field(..., max_length=50)
    # Datos de usuario (requeridos)
    apellidos: str = Field(..., min_length=1, max_length=100, description="Apellidos del cliente")
    nombres: str = Field(..., min_length=1, max_length=100, description="Nombres del cliente")
    correo: EmailStr = Field(..., description="Correo electrónico (será el usuario)")
    celular: Optional[str] = Field(None, max_length=20)
    password: str = Field(..., min_length=6, description="Contraseña del usuario")


class ClienteUpdate(BaseModel):
    direccion: Optional[str] = Field(None, max_length=300)
    # Datos de usuario
    apellidos: Optional[str] = Field(None, max_length=100)
    nombres: Optional[str] = Field(None, max_length=100)
    correo: Optional[EmailStr] = None
    celular: Optional[str] = Field(None, max_length=20)
    password: Optional[str] = Field(None, min_length=6, description="Nueva contraseña (opcional)")


class ClienteResponse(ClienteBase):
    cod_cliente: str
    cod_usuario: int
    # Datos de usuario
    apellidos: Optional[str] = None
    nombres: Optional[str] = None
    correo: Optional[str] = None
    celular: Optional[str] = None
    estado: Optional[int] = None

    class Config:
        from_attributes = True
