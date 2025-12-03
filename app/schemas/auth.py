"""
Schemas Pydantic para Autenticación
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


class MeResponse(UsuarioBase):
    cod_usuario: int
    fecha_ingreso: date
    estado: int
    fecha_baja: Optional[date] = None
    cod_cliente: Optional[str] = Field(None, examples=["CLI001"])
    email_verificado: int = Field(default=0, description="0=No verificado, 1=Verificado")

    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    correo: EmailStr
    password: str
    nivel: int = Field(..., ge=1, le=3, description="1=Supervisor, 2=Vendedor, 3=Cliente")


class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    usuario: MeResponse
    num_sesion: int


class LogoutResponse(BaseModel):
    message: str


class VerifyEmailRequest(BaseModel):
    token: str = Field(..., min_length=1, description="Token de verificación de email")


class VerifyEmailResponse(BaseModel):
    message: str
    email_verified: bool
