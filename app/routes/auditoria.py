from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.sesion_log import SesionLog
from app.models.detalle_sesion import DetalleSesion
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.schemas.auditoria import SesionLogResponse, DetalleSesionResponse, ActividadUsuario, SesionLogList
from app.core.security import registrar_auditoria, get_token

router = APIRouter(
    prefix="/auditoria",
    tags=["Auditoría"],
)

@router.get("/sesiones", response_model=List[SesionLogList])
def list_sesiones(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    estado: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """
    Listar sesiones con filtros (Optimizado: solo cuenta acciones)
    """
    # Consulta base
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

    resultados = []
    for sesion in sesiones:
        sesion_dict = {
            "num_sesion": sesion.num_sesion,
            "fecha_inicio": sesion.fecha_inicio,
            "fecha_fin": sesion.fecha_fin,
            "estado": sesion.estado,
            "cod_usuario": None,
            "nombre_usuario": "Desconocido",
            "correo_usuario": None,
            "total_acciones": len(sesion.detalles) # Contamos en memoria ya que joinedload trae todo
        }

        if sesion.detalles:
            primer_detalle = sesion.detalles[0]
            if primer_detalle.usuario:
                sesion_dict["cod_usuario"] = primer_detalle.usuario.cod_usuario
                sesion_dict["nombre_usuario"] = f"{primer_detalle.usuario.nombres} {primer_detalle.usuario.apellidos}"
                sesion_dict["correo_usuario"] = primer_detalle.usuario.correo
        
        resultados.append(sesion_dict)
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "sesion_log", 0)

    return resultados

@router.get("/acciones", response_model=List[DetalleSesionResponse])
def list_acciones(
    cod_usuario: Optional[int] = None,
    tabla: Optional[str] = None,
    accion: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """
    Listar acciones individuales (DetalleSesion) para rollback
    """
    query = db.query(DetalleSesion).options(
        joinedload(DetalleSesion.usuario)
    )

    if cod_usuario:
        query = query.filter(DetalleSesion.cod_usuario == cod_usuario)
    if tabla:
        query = query.filter(DetalleSesion.tabla == tabla)
    if accion is not None:
        query = query.filter(DetalleSesion.accion == accion)
    else:
        # Excluir consultas (0) y rollbacks (4) por defecto para limpiar la vista
        query = query.filter(DetalleSesion.accion.notin_([0, 4]))

    # Ordenar por fecha desc (usando hora y num_sesion/num_detalle como proxy de tiempo)
    # Lo ideal sería tener fecha en detalle, pero está en sesión.
    # Podemos hacer join con sesión para ordenar por fecha.
    query = query.join(DetalleSesion.sesion).order_by(SesionLog.fecha_inicio.desc(), DetalleSesion.hora.desc())

    detalles = query.offset(skip).limit(limit).all()
    
    resultados = []
    for d in detalles:
        resultados.append({
            "num_detalle": d.num_detalle,
            "tabla": d.tabla,
            "accion": d.accion,
            "hora": d.hora,
            "datos_json": d.datos_json,
            "cod_usuario": d.cod_usuario,
            "num_sesion": d.num_sesion,
            "rollback_realizado": d.rollback_realizado,
            "nombre_usuario": f"{d.usuario.nombres} {d.usuario.apellidos}" if d.usuario else "Desconocido",
            "accion_text": ["Consulta", "Edición", "Inserción", "Eliminación", "Rollback"][d.accion] if 0 <= d.accion <= 4 else "Desconocido"
        })

    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "detalle_sesion", 0)

    return resultados

@router.get("/sesiones/{num_sesion}", response_model=SesionLogResponse)
def get_sesion(
    num_sesion: int, 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
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
        
        
        # Ordenar detalles por hora descendente (más reciente primero)
        detalles_ordenados = sorted(sesion.detalles, key=lambda d: d.hora if d.hora else datetime.min.time(), reverse=True)
        
        for d in detalles_ordenados:
            detalle_dict = {
                "num_detalle": d.num_detalle,
                "tabla": d.tabla,
                "accion": d.accion,
                "hora": d.hora,
                "cod_usuario": d.cod_usuario,
                "num_sesion": d.num_sesion,
                "rollback_realizado": d.rollback_realizado,
                "nombre_usuario": f"{d.usuario.nombres} {d.usuario.apellidos}" if d.usuario else None,
                "accion_text": ["Consulta", "Edición", "Inserción", "Eliminación", "Rollback"][d.accion] if 0 <= d.accion <= 4 else "Desconocido"
            }
            sesion_dict["detalles"].append(detalle_dict)
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "sesion_log", 0)

    return sesion_dict


import json
from datetime import datetime
from app.routes.rollback.rollback_usuarios import rollback_usuario
from app.routes.rollback.rollback_clientes import rollback_cliente
from app.routes.rollback.rollback_pedidos import rollback_pedido
from app.routes.rollback.rollback_ofertas import rollback_oferta

@router.post("/rollback/{num_detalle}")
def rollback_accion(
    num_detalle: int,
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """
    Revertir una acción específica (Rollback)
    """
    detalle = db.query(DetalleSesion).filter(DetalleSesion.num_detalle == num_detalle).first()
    if not detalle:
        raise HTTPException(status_code=404, detail="Detalle de auditoría no encontrado")
    
    # Verificar que no se haya hecho rollback ya
    if detalle.rollback_realizado == 1:
        raise HTTPException(status_code=400, detail="Esta acción ya fue revertida mediante rollback")
        
    if not detalle.datos_json:
        raise HTTPException(status_code=400, detail="No hay datos de snapshot para realizar rollback")
        
    try:
        snapshot = json.loads(detalle.datos_json)
        # Soporte para estructura antigua y nueva
        if "old_data" in snapshot or "new_data" in snapshot:
            old_data = snapshot.get("old_data")
            new_data = snapshot.get("new_data")
            # Para rollback usamos old_data si es edición/eliminación, o new_data si es inserción (para obtener ID)
            datos = old_data if detalle.accion in [1, 3] else new_data
        else:
            # Estructura antigua (directa)
            datos = snapshot
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error al decodificar snapshot de datos")
        
    if not datos and detalle.accion != 0: # Consulta no necesita datos
         raise HTTPException(status_code=400, detail="Snapshot de datos vacío, no se puede realizar rollback")

    # Lógica de Rollback delegada a módulos
    mensaje = ""
    
    if detalle.tabla == "usuario":
        mensaje = rollback_usuario(db, detalle.accion, datos)
    elif detalle.tabla == "cliente":
        mensaje = rollback_cliente(db, detalle.accion, datos)
    elif detalle.tabla == "pedido":
        mensaje = rollback_pedido(db, detalle.accion, datos)
    elif detalle.tabla == "oferta":
        mensaje = rollback_oferta(db, detalle.accion, datos)
    else:
        raise HTTPException(status_code=400, detail=f"Tabla {detalle.tabla} no soportada para rollback aún")

    # Marcar la acción original como rollback realizado
    detalle.rollback_realizado = 1
    
    # Registrar auditoría del rollback con acción tipo 4 (rollback)
    registrar_auditoria(db, token, detalle.tabla, 4, new_data={"rollback_ref": num_detalle, "message": mensaje})
    
    db.commit()
    return {"message": mensaje}
