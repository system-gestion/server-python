from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from app.models.usuario import Usuario

def rollback_usuario(db: Session, accion: int, datos: dict) -> str:
    """
    Lógica de rollback para la tabla 'usuario'
    """
    # Rollback de Inserción (2) -> Eliminar registro creado
    if accion == 2:
        cod_usuario = datos.get("cod_usuario")
        if not cod_usuario:
            raise HTTPException(status_code=400, detail="Snapshot incompleto (falta ID)")
            
        usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
        if usuario:
            db.delete(usuario)
            return f"Rollback: Usuario {cod_usuario} eliminado (reversión de inserción)"
        else:
            return f"Rollback: Usuario {cod_usuario} ya no existe, nada que hacer"
            
    # Rollback de Edición (1) -> Restaurar valores originales
    elif accion == 1:
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
        
        return f"Rollback: Usuario {usuario.cod_usuario} restaurado a estado previo"

    # Rollback de Eliminación (3) -> Re-insertar registro
    elif accion == 3:
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
        return f"Rollback: Usuario {datos.get('cod_usuario')} restaurado (reversión de eliminación)"
        
    else:
        raise HTTPException(status_code=400, detail=f"Acción {accion} no soportada para rollback")
