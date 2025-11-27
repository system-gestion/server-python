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

from app.models.pedido import Pedido
from app.models.detalle_pedido import DetallePedido
from datetime import datetime

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

    # Lógica de Rollback según tabla y acción
    # Lógica de Rollback según tabla y acción
    if detalle.tabla == "usuario":
        # Rollback de Inserción (2) -> Eliminar registro creado
        if detalle.accion == 2:
            cod_usuario = datos.get("cod_usuario")
            if not cod_usuario:
                raise HTTPException(status_code=400, detail="Snapshot incompleto (falta ID)")
                
            usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
            if usuario:
                db.delete(usuario)
                mensaje = f"Rollback: Usuario {cod_usuario} eliminado (reversión de inserción)"
            else:
                mensaje = f"Rollback: Usuario {cod_usuario} ya no existe, nada que hacer"
                
        # Rollback de Edición (1) -> Restaurar valores originales
        elif detalle.accion == 1:
            # Intentar obtener ID del snapshot
            cod_usuario_target = datos.get("cod_usuario")
            usuario = None
            
            if cod_usuario_target:
                usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario_target).first()
            
            # Fallback: buscar por correo si no hay ID (para compatibilidad con snapshots viejos si los hubiera)
            if not usuario and datos.get("correo"):
                usuario = db.query(Usuario).filter(Usuario.correo == datos.get("correo")).first()
            
            if not usuario:
                 raise HTTPException(status_code=400, detail="No se pudo identificar el registro afectado para rollback")

            for key, value in datos.items():
                if hasattr(usuario, key) and key != "cod_usuario": # No actualizamos la PK
                    # Manejo de fechas
                    if key in ["fecha_ingreso", "fecha_baja"] and isinstance(value, str):
                        try:
                            if value == "None":
                                value = None
                            else:
                                value = datetime.strptime(value, "%Y-%m-%d").date()
                        except:
                            pass # Mantener como string o lo que sea si falla
                    setattr(usuario, key, value)
            
            mensaje = f"Rollback: Usuario {usuario.cod_usuario} restaurado a estado previo"

        # Rollback de Eliminación (3) -> Re-insertar registro
        elif detalle.accion == 3:
            # Convertir fechas de string a date
            if "fecha_ingreso" in datos and isinstance(datos["fecha_ingreso"], str):
                 try:
                     datos["fecha_ingreso"] = datetime.strptime(datos["fecha_ingreso"], "%Y-%m-%d").date()
                 except:
                     pass
            if "fecha_baja" in datos and isinstance(datos["fecha_baja"], str):
                 if datos["fecha_baja"] == "None":
                     datos["fecha_baja"] = None
                 else:
                     try:
                         datos["fecha_baja"] = datetime.strptime(datos["fecha_baja"], "%Y-%m-%d").date()
                     except:
                         datos["fecha_baja"] = None
            
            nuevo_usuario = Usuario(**datos)
            db.add(nuevo_usuario)
            mensaje = f"Rollback: Usuario {datos.get('cod_usuario')} restaurado (reversión de eliminación)"
            
        else:
            raise HTTPException(status_code=400, detail=f"Acción {detalle.accion} no soportada para rollback")

    elif detalle.tabla == "cliente":
        # Rollback de Inserción (2) -> Eliminar cliente y usuario
        if detalle.accion == 2:
            cod_cliente = datos.get("cod_cliente")
            cliente = db.query(Cliente).filter(Cliente.cod_cliente == cod_cliente).first()
            if cliente:
                cod_usuario = cliente.cod_usuario
                db.delete(cliente)
                
                # Eliminar usuario también si existe
                usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
                if usuario:
                    db.delete(usuario)
                    
                mensaje = f"Rollback: Cliente {cod_cliente} y Usuario asociado eliminados"
            else:
                mensaje = f"Rollback: Cliente {cod_cliente} ya no existe"

        # Rollback de Edición (1) -> Restaurar
        elif detalle.accion == 1:
            cod_cliente = datos.get("cod_cliente")
            cliente = db.query(Cliente).filter(Cliente.cod_cliente == cod_cliente).first()
            if not cliente:
                 raise HTTPException(status_code=400, detail="Cliente no encontrado")
            
            # Restaurar datos cliente
            if "nombre" in datos: cliente.nombre = datos["nombre"]
            if "direccion" in datos: cliente.direccion = datos["direccion"]
            if "telefono" in datos: cliente.telefono = datos["telefono"]
            
            # Restaurar datos usuario si existen en el snapshot
            if cliente.usuario:
                if "correo" in datos and datos["correo"]:
                    cliente.usuario.correo = datos["correo"]
                if "celular" in datos and datos["celular"]:
                    cliente.usuario.celular = datos["celular"]
                
                # Sincronizar nombre usuario si cambió
                if "nombre" in datos:
                    nombre_completo = datos["nombre"].strip().split()
                    cliente.usuario.apellidos = nombre_completo[0] if len(nombre_completo) > 0 else ""
                    cliente.usuario.nombres = " ".join(nombre_completo[1:]) if len(nombre_completo) > 1 else nombre_completo[0] if len(nombre_completo) == 1 else ""

            mensaje = f"Rollback: Cliente {cod_cliente} restaurado"

        # Rollback de Eliminación (3) -> Recrear
        elif detalle.accion == 3:
             cod_usuario = datos.get("cod_usuario")
             usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
             
             if usuario:
                 usuario.estado = 1 # Reactivar usuario
             
             # Recrear cliente
             cliente_data = {k: v for k, v in datos.items() if k in ["cod_cliente", "nombre", "direccion", "telefono", "cod_usuario"]}
             nuevo_cliente = Cliente(**cliente_data)
             db.add(nuevo_cliente)
             
             mensaje = f"Rollback: Cliente {datos.get('cod_cliente')} restaurado"
             
        else:
            raise HTTPException(status_code=400, detail=f"Acción {detalle.accion} no soportada")

    elif detalle.tabla == "pedido":
        # Rollback Inserción (2)
        if detalle.accion == 2:
            num_pedido = datos.get("num_pedido")
            if not num_pedido:
                raise HTTPException(status_code=400, detail="Snapshot incompleto (falta ID)")
            
            pedido = db.query(Pedido).filter(Pedido.num_pedido == num_pedido).first()
            if pedido:
                db.delete(pedido)
                mensaje = f"Rollback: Pedido {num_pedido} eliminado (reversión de inserción)"
            else:
                mensaje = f"Rollback: Pedido {num_pedido} ya no existe"

        # Rollback Edición (1)
        elif detalle.accion == 1:
            num_pedido = datos.get("num_pedido")
            pedido = db.query(Pedido).filter(Pedido.num_pedido == num_pedido).first()
            
            if not pedido:
                raise HTTPException(status_code=400, detail="Pedido no encontrado para rollback")

            # Restore fields
            for key, value in datos.items():
                if hasattr(pedido, key) and key != "num_pedido" and key != "was_cancelled":
                    # Convert date strings back to date objects if needed
                    if key in ["fecha", "fecha_entrega"] and isinstance(value, str):
                        try:
                            value = datetime.strptime(value, "%Y-%m-%d").date()
                        except ValueError:
                            pass # Keep as string if format fails, let SQLAlchemy handle or fail
                    setattr(pedido, key, value)
            
            # Special handling for un-cancelling
            if pedido.estado != 3:
                 db.query(DetallePedido).filter(DetallePedido.num_pedido == num_pedido).update({"estado": 1})

            mensaje = f"Rollback: Pedido {num_pedido} restaurado a estado previo"

        # Rollback Eliminación (3)
        elif detalle.accion == 3:
            pedido_data = datos.copy()
            detalles_data = pedido_data.pop("detalles", [])
            
            # Remove extra fields
            pedido_data.pop("nombre_cliente", None)
            
            # Convert dates
            if "fecha" in pedido_data and isinstance(pedido_data["fecha"], str):
                 pedido_data["fecha"] = datetime.strptime(pedido_data["fecha"], "%Y-%m-%d").date()
            if "fecha_entrega" in pedido_data and isinstance(pedido_data["fecha_entrega"], str):
                 pedido_data["fecha_entrega"] = datetime.strptime(pedido_data["fecha_entrega"], "%Y-%m-%d").date()

            # Create Pedido
            nuevo_pedido = Pedido(**pedido_data)
            db.add(nuevo_pedido)
            db.flush() 
            
            # Create Detalles
            for d_data in detalles_data:
                d_data.pop("nombre_articulo", None)
                d_data.pop("pvp", None)
                nuevo_detalle = DetallePedido(**d_data)
                db.add(nuevo_detalle)
                
            mensaje = f"Rollback: Pedido {datos.get('num_pedido')} restaurado (reversión de eliminación)"
            
        else:
             raise HTTPException(status_code=400, detail=f"Acción {detalle.accion} no soportada")

    else:
        raise HTTPException(status_code=400, detail=f"Tabla {detalle.tabla} no soportada para rollback aún")

    # Marcar la acción original como rollback realizado
    detalle.rollback_realizado = 1
    
    # Registrar auditoría del rollback con acción tipo 4 (rollback)
    registrar_auditoria(db, token, detalle.tabla, 4, new_data={"rollback_ref": num_detalle, "message": mensaje})
    
    db.commit()
    return {"message": mensaje}
