"""
Rutas de Auditoría
Consulta de sesiones y acciones de usuarios
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.sesion_log import SesionLog
from app.models.detalle_sesion import DetalleSesion
from app.models.usuario import Usuario
from app.schemas.auditoria import (
    SesionLogResponse, DetalleSesionResponse, ActividadUsuario
)

router = APIRouter(
    prefix="/auditoria",
    tags=["Auditoría"],
)


@router.get("/sesiones", response_model=List[SesionLogResponse])
def listar_sesiones(
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicial del rango de búsqueda de sesiones"),
    fecha_fin: Optional[date] = Query(None, description="Fecha final del rango de búsqueda de sesiones"),
    estado: Optional[int] = Query(None, ge=0, le=1, description="Estado de la sesión (0: cerrada, 1: activa)"),
    skip: int = Query(0, description="Número de registros a omitir para paginación"),
    limit: int = Query(100, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db)
):
    """Listar sesiones con filtros"""
    query = db.query(SesionLog).options(joinedload(SesionLog.detalles))
    
    if fecha_inicio:
        query = query.filter(SesionLog.fecha_inicio >= fecha_inicio)
    if fecha_fin:
        query = query.filter(SesionLog.fecha_inicio <= fecha_fin)
    if estado is not None:
        query = query.filter(SesionLog.estado == estado)
    
    sesiones = query.offset(skip).limit(limit).all()
    
    resultado = []
    for sesion in sesiones:
        if sesion.detalles:
            cod_usuario = sesion.detalles[0].cod_usuario
            usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
            nombre_usuario = f"{usuario.nombres} {usuario.apellidos}" if usuario else None
        else:
            cod_usuario = None
            nombre_usuario = None
        
        resultado.append({
            "num_sesion": sesion.num_sesion,
            "fecha_inicio": sesion.fecha_inicio,
            "fecha_fin": sesion.fecha_fin,
            "estado": sesion.estado,
            "cod_usuario": cod_usuario,
            "nombre_usuario": nombre_usuario,
            "detalles": [_format_detalle(d, db) for d in sesion.detalles]
        })
    
    return resultado


@router.get("/sesiones/{num_sesion}", response_model=SesionLogResponse)
def obtener_sesion(num_sesion: int = Path(..., description="Número único de la sesión"), db: Session = Depends(get_db)):
    """Obtener detalle de una sesión específica"""
    sesion = db.query(SesionLog).options(
        joinedload(SesionLog.detalles)
    ).filter(SesionLog.num_sesion == num_sesion).first()
    
    if not sesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sesión {num_sesion} no encontrada"
        )
    
    if sesion.detalles:
        cod_usuario = sesion.detalles[0].cod_usuario
        usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
        nombre_usuario = f"{usuario.nombres} {usuario.apellidos}" if usuario else None
    else:
        cod_usuario = None
        nombre_usuario = None
    
    return {
        "num_sesion": sesion.num_sesion,
        "fecha_inicio": sesion.fecha_inicio,
        "fecha_fin": sesion.fecha_fin,
        "estado": sesion.estado,
        "cod_usuario": cod_usuario,
        "nombre_usuario": nombre_usuario,
        "detalles": [_format_detalle(d, db) for d in sesion.detalles]
    }


@router.get("/acciones", response_model=List[DetalleSesionResponse])
def listar_acciones(
    cod_usuario: Optional[int] = Query(None, description="Código del usuario para filtrar acciones"),
    tabla: Optional[str] = Query(None, description="Nombre de la tabla para filtrar acciones"),
    accion: Optional[int] = Query(None, ge=0, le=3, description="Tipo de acción (0: Consulta, 1: Edición, 2: Inserción, 3: Eliminación)"),
    skip: int = Query(0, description="Número de registros a omitir para paginación"),
    limit: int = Query(100, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db)
):
    """Listar acciones de usuarios con filtros"""
    query = db.query(DetalleSesion)
    
    if cod_usuario:
        query = query.filter(DetalleSesion.cod_usuario == cod_usuario)
    if tabla:
        query = query.filter(DetalleSesion.tabla == tabla)
    if accion is not None:
        query = query.filter(DetalleSesion.accion == accion)
    
    detalles = query.offset(skip).limit(limit).all()
    return [_format_detalle(d, db) for d in detalles]


@router.get("/usuarios/{cod_usuario}/actividad", response_model=ActividadUsuario)
def actividad_usuario(cod_usuario: int = Path(..., description="Código del usuario para obtener su actividad"), db: Session = Depends(get_db)):
    """Obtener resumen de actividad de un usuario"""
    usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {cod_usuario} no encontrado"
        )
    
    # Contar sesiones
    total_sesiones = db.query(SesionLog).join(
        DetalleSesion
    ).filter(DetalleSesion.cod_usuario == cod_usuario).distinct().count()
    
    sesiones_activas = db.query(SesionLog).join(
        DetalleSesion
    ).filter(
        and_(
            DetalleSesion.cod_usuario == cod_usuario,
            SesionLog.estado == 1
        )
    ).distinct().count()
    
    # Contar acciones
    total_acciones = db.query(DetalleSesion).filter(
        DetalleSesion.cod_usuario == cod_usuario
    ).count()
    
    # Última sesión
    ultima_sesion = db.query(SesionLog).join(
        DetalleSesion
    ).filter(
        DetalleSesion.cod_usuario == cod_usuario
    ).order_by(SesionLog.fecha_inicio.desc()).first()
    
    return {
        "cod_usuario": usuario.cod_usuario,
        "nombre_usuario": f"{usuario.nombres} {usuario.apellidos}",
        "total_sesiones": total_sesiones,
        "sesiones_activas": sesiones_activas,
        "total_acciones": total_acciones,
        "ultima_sesion": ultima_sesion.fecha_inicio if ultima_sesion else None
    }


@router.get("/resumen", response_model=List[ActividadUsuario])
def resumen_actividades(db: Session = Depends(get_db)):
    """Obtener resumen de actividad de todos los usuarios"""
    usuarios = db.query(Usuario).filter(Usuario.estado == 1).all()
    
    resultado = []
    for usuario in usuarios:
        total_sesiones = db.query(SesionLog).join(
            DetalleSesion
        ).filter(DetalleSesion.cod_usuario == usuario.cod_usuario).distinct().count()
        
        sesiones_activas = db.query(SesionLog).join(
            DetalleSesion
        ).filter(
            and_(
                DetalleSesion.cod_usuario == usuario.cod_usuario,
                SesionLog.estado == 1
            )
        ).distinct().count()
        
        total_acciones = db.query(DetalleSesion).filter(
            DetalleSesion.cod_usuario == usuario.cod_usuario
        ).count()
        
        ultima_sesion = db.query(SesionLog).join(
            DetalleSesion
        ).filter(
            DetalleSesion.cod_usuario == usuario.cod_usuario
        ).order_by(SesionLog.fecha_inicio.desc()).first()
        
        resultado.append({
            "cod_usuario": usuario.cod_usuario,
            "nombre_usuario": f"{usuario.nombres} {usuario.apellidos}",
            "total_sesiones": total_sesiones,
            "sesiones_activas": sesiones_activas,
            "total_acciones": total_acciones,
            "ultima_sesion": ultima_sesion.fecha_inicio if ultima_sesion else None
        })
    
    return resultado


def _format_detalle(detalle: DetalleSesion, db: Session) -> dict:
    """Helper para formatear detalle de sesión"""
    usuario = db.query(Usuario).filter(
        Usuario.cod_usuario == detalle.cod_usuario
    ).first()
    
    acciones = {0: "Consulta", 1: "Edición", 2: "Inserción", 3: "Eliminación"}
    
    return {
        "num_detalle": detalle.num_detalle,
        "tabla": detalle.tabla,
        "accion": detalle.accion,
        "cod_usuario": detalle.cod_usuario,
        "num_sesion": detalle.num_sesion,
        "nombre_usuario": f"{usuario.nombres} {usuario.apellidos}" if usuario else None,
        "accion_text": acciones.get(detalle.accion, "Desconocida")
    }
