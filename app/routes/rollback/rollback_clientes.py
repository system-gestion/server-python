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
        if "direccion" in datos: 
            cliente.direccion = datos["direccion"]
        
        # Restaurar datos usuario si existen en el snapshot
        if cliente.usuario:
            if "apellidos" in datos and datos["apellidos"]:
                cliente.usuario.apellidos = datos["apellidos"]
            if "nombres" in datos and datos["nombres"]:
                cliente.usuario.nombres = datos["nombres"]
            if "correo" in datos and datos["correo"]:
                cliente.usuario.correo = datos["correo"]
            if "celular" in datos and datos["celular"]:
                cliente.usuario.celular = datos["celular"]

        return f"Rollback: Cliente {cod_cliente} restaurado"

    # Rollback de Eliminación (3) -> Recrear
    elif accion == 3:
            cod_usuario = datos.get("cod_usuario")
            usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
            
            if usuario:
                usuario.estado = 1 # Reactivar usuario
            
            # Recrear cliente (solo con direccion y cod_usuario)
            cliente_data = {k: v for k, v in datos.items() if k in ["cod_cliente", "direccion", "cod_usuario"]}
            nuevo_cliente = Cliente(**cliente_data)
            db.add(nuevo_cliente)
            
            return f"Rollback: Cliente {datos.get('cod_cliente')} restaurado"
            
    else:
        raise HTTPException(status_code=400, detail=f"Acción {accion} no soportada")
