"""
Schemas Pydantic para Usuario
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional


class UsuarioBase(BaseModel):
    apellidos: str = Field(..., min_length=1, max_length=100)
    nombres: str = Field(..., min_length=1, max_length=100)
    nivel: int = Field(..., ge=1, le=3, description="1=Supervisor, 2=Vendedor, 3=Cliente")
    correo: EmailStr
    celular: Optional[str] = Field(None, max_length=20)


class UsuarioCreate(UsuarioBase):
    cod_usuario: int
    password: str = Field(..., min_length=6)


class UsuarioUpdate(BaseModel):
    apellidos: Optional[str] = Field(None, max_length=100)
    nombres: Optional[str] = Field(None, max_length=100)
    nivel: Optional[int] = Field(None, ge=1, le=3)
    correo: Optional[EmailStr] = None
    celular: Optional[str] = Field(None, max_length=20)
    password: Optional[str] = Field(None, min_length=6)
    estado: Optional[int] = Field(None, ge=0, le=1)


class UsuarioResponse(UsuarioBase):
    cod_usuario: int
    fecha_ingreso: date
    estado: int
    fecha_baja: Optional[date] = None

    class Config:
        from_attributes = True


class UsuarioOnline(BaseModel):
    cod_usuario: int
    nombres: str
    apellidos: str
    correo: str
    nivel: int
    sesion_activa: bool
    ultima_actividad: Optional[date] = None

    class Config:
        from_attributes = True
