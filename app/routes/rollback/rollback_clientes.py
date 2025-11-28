from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.cliente import Cliente
from app.models.usuario import Usuario

def rollback_cliente(db: Session, accion: int, datos: dict) -> str:
    """
    Lógica de rollback para la tabla 'cliente'
    """
    # Rollback de Inserción (2) -> Eliminar cliente y usuario
    if accion == 2:
        cod_cliente = datos.get("cod_cliente")
        cliente = db.query(Cliente).filter(Cliente.cod_cliente == cod_cliente).first()
        if cliente:
            cod_usuario = cliente.cod_usuario
            db.delete(cliente)
            
            # Eliminar usuario también si existe
            usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
            if usuario:
                db.delete(usuario)
                
            return f"Rollback: Cliente {cod_cliente} y Usuario asociado eliminados"
        else:
            return f"Rollback: Cliente {cod_cliente} ya no existe"

    # Rollback de Edición (1) -> Restaurar
    elif accion == 1:
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

        return f"Rollback: Cliente {cod_cliente} restaurado"

    # Rollback de Eliminación (3) -> Recrear
    elif accion == 3:
            cod_usuario = datos.get("cod_usuario")
            usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
            
            if usuario:
                usuario.estado = 1 # Reactivar usuario
            
            # Recrear cliente
            cliente_data = {k: v for k, v in datos.items() if k in ["cod_cliente", "nombre", "direccion", "telefono", "cod_usuario"]}
            nuevo_cliente = Cliente(**cliente_data)
            db.add(nuevo_cliente)
            
            return f"Rollback: Cliente {datos.get('cod_cliente')} restaurado"
            
    else:
        raise HTTPException(status_code=400, detail=f"Acción {accion} no soportada")
