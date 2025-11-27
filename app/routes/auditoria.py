from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.sesion_log import SesionLog
from app.models.detalle_sesion import DetalleSesion
from app.models.usuario import Usuario
from app.schemas.auditoria import SesionLogResponse, DetalleSesionResponse, ActividadUsuario

router = APIRouter(
    prefix="/auditoria",
    tags=["Auditoría"],
)

@router.get("/sesiones", response_model=List[SesionLogResponse])
def list_sesiones(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    estado: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Listar sesiones con filtros
    """
    query = db.query(SesionLog).options(
        joinedload(SesionLog.detalles).joinedload(DetalleSesion.usuario)
    )

    if fecha_inicio:
        query = query.filter(SesionLog.fecha_inicio >= fecha_inicio)
    if fecha_fin:
        query = query.filter(SesionLog.fecha_inicio <= fecha_fin)
    if estado is not None:
        query = query.filter(SesionLog.estado == estado)

    # Ordenar por fecha inicio descendente
    query = query.order_by(SesionLog.fecha_inicio.desc(), SesionLog.num_sesion.desc())

    sesiones = query.offset(skip).limit(limit).all()

    # Procesar para agregar info de usuario
    resultados = []
    for sesion in sesiones:
        # Convertir a dict para poder modificar
        sesion_dict = {
            "num_sesion": sesion.num_sesion,
            "fecha_inicio": sesion.fecha_inicio,
            "fecha_fin": sesion.fecha_fin,
            "estado": sesion.estado,
            "detalles": [],
            "cod_usuario": None,
            "nombre_usuario": "Desconocido",
            "correo_usuario": None
        }

        # Intentar obtener usuario del primer detalle
        if sesion.detalles:
            primer_detalle = sesion.detalles[0]
            if primer_detalle.usuario:
                sesion_dict["cod_usuario"] = primer_detalle.usuario.cod_usuario
                sesion_dict["nombre_usuario"] = f"{primer_detalle.usuario.nombres} {primer_detalle.usuario.apellidos}"
                sesion_dict["correo_usuario"] = primer_detalle.usuario.correo
            
            # Mapear detalles
            for d in sesion.detalles:
                detalle_dict = {
                    "num_detalle": d.num_detalle,
                    "tabla": d.tabla,
                    "accion": d.accion,
                    "cod_usuario": d.cod_usuario,
                    "num_sesion": d.num_sesion,
                    "nombre_usuario": f"{d.usuario.nombres} {d.usuario.apellidos}" if d.usuario else None,
                    "accion_text": ["Consulta", "Edición", "Inserción", "Eliminación"][d.accion] if 0 <= d.accion <= 3 else "Desconocido"
                }
                sesion_dict["detalles"].append(detalle_dict)
        
        resultados.append(sesion_dict)

    return resultados

@router.get("/sesiones/{num_sesion}", response_model=SesionLogResponse)
def get_sesion(num_sesion: int, db: Session = Depends(get_db)):
    """
    Obtener detalle de una sesión
    """
    sesion = db.query(SesionLog).options(
        joinedload(SesionLog.detalles).joinedload(DetalleSesion.usuario)
    ).filter(SesionLog.num_sesion == num_sesion).first()

    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    sesion_dict = {
        "num_sesion": sesion.num_sesion,
        "fecha_inicio": sesion.fecha_inicio,
        "fecha_fin": sesion.fecha_fin,
        "estado": sesion.estado,
        "detalles": [],
        "cod_usuario": None,
        "nombre_usuario": "Desconocido",
        "correo_usuario": None
    }

    if sesion.detalles:
        primer_detalle = sesion.detalles[0]
        if primer_detalle.usuario:
            sesion_dict["cod_usuario"] = primer_detalle.usuario.cod_usuario
            sesion_dict["nombre_usuario"] = f"{primer_detalle.usuario.nombres} {primer_detalle.usuario.apellidos}"
            sesion_dict["correo_usuario"] = primer_detalle.usuario.correo
        
        for d in sesion.detalles:
            detalle_dict = {
                "num_detalle": d.num_detalle,
                "tabla": d.tabla,
                "accion": d.accion,
                "cod_usuario": d.cod_usuario,
                "num_sesion": d.num_sesion,
                "nombre_usuario": f"{d.usuario.nombres} {d.usuario.apellidos}" if d.usuario else None,
                "accion_text": ["Consulta", "Edición", "Inserción", "Eliminación"][d.accion] if 0 <= d.accion <= 3 else "Desconocido"
            }
            sesion_dict["detalles"].append(detalle_dict)

    return sesion_dict
