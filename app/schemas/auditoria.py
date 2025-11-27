"""
Schemas Pydantic para Auditoría (SesionLog y DetalleSesion)
"""
from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional, List


class DetalleSesionBase(BaseModel):
    tabla: str = Field(..., max_length=100)
    accion: int = Field(..., ge=0, le=3, description="0=Consulta, 1=Edición, 2=Inserción, 3=Eliminación")
    hora: Optional[time] = None
    datos_json: Optional[str] = None
    cod_usuario: int
    num_sesion: int


class DetalleSesionCreate(DetalleSesionBase):
    pass


class DetalleSesionResponse(DetalleSesionBase):
    num_detalle: int
    nombre_usuario: Optional[str] = None
    accion_text: Optional[str] = None
    datos_json: Optional[str] = None

    class Config:
        from_attributes = True


class SesionLogBase(BaseModel):
    fecha_inicio: date = Field(default_factory=date.today)
    fecha_fin: Optional[date] = None
    estado: int = Field(default=1, ge=0, le=1)


class SesionLogCreate(SesionLogBase):
    num_sesion: int
    cod_usuario: int


class SesionLogResponse(SesionLogBase):
    num_sesion: int
    cod_usuario: Optional[int] = None
    nombre_usuario: Optional[str] = None
    correo_usuario: Optional[str] = None
    detalles: List[DetalleSesionResponse] = []

    class Config:
        from_attributes = True

class SesionLogList(SesionLogBase):
    num_sesion: int
    cod_usuario: Optional[int] = None
    nombre_usuario: Optional[str] = None
    correo_usuario: Optional[str] = None
    total_acciones: int = 0

    class Config:
        from_attributes = True


class ActividadUsuario(BaseModel):
    cod_usuario: int
    nombre_usuario: str
    total_sesiones: int
    sesiones_activas: int
    total_acciones: int
    ultima_sesion: Optional[date] = None
