"""
Rutas CRUD para Clientes
Maneja la creación/actualización de Usuario y Cliente de forma sincronizada
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List
from datetime import date
import bcrypt

from app.database import get_db
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse
from app.core.security import registrar_auditoria, get_token

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
)


@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def crear_cliente(
    cliente: ClienteCreate, 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """
    Crear nuevo cliente y su usuario asociado (nivel 3)
    """
    # Verificar si el código de cliente ya existe
    if db.query(Cliente).filter(Cliente.cod_cliente == cliente.cod_cliente).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cliente {cliente.cod_cliente} ya existe"
        )
    
    # Verificar si el correo ya existe
    if db.query(Usuario).filter(Usuario.correo == cliente.correo).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El correo {cliente.correo} ya está registrado"
        )
    
    # Crear usuario (nivel 3 = Cliente)
    # Hash password
    hashed_password = bcrypt.hashpw(cliente.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    nuevo_usuario = Usuario(
        apellidos=cliente.apellidos,
        nombres=cliente.nombres,
        nivel=3,  # Cliente
        correo=cliente.correo,
        celular=cliente.celular,
        fecha_ingreso=date.today(),
        estado=1,  # Activo
        password=hashed_password
    )
    db.add(nuevo_usuario)
    db.flush()  # Para obtener el cod_usuario
    
    # Crear cliente
    nuevo_cliente = Cliente(
        cod_cliente=cliente.cod_cliente,
        direccion=cliente.direccion,
        cod_usuario=nuevo_usuario.cod_usuario
    )
    db.add(nuevo_cliente)
    
    # Registrar auditoría (2 = Inserción)
    registrar_auditoria(db, token, "cliente", 2, new_data={
        "cod_cliente": cliente.cod_cliente,
        "apellidos": cliente.apellidos,
        "nombres": cliente.nombres,
        "correo": cliente.correo,
        "cod_usuario": nuevo_usuario.cod_usuario
    })
    
    db.commit()
    db.refresh(nuevo_cliente)
    db.refresh(nuevo_usuario)
    
    # Retornar con datos del usuario
    return ClienteResponse(
        cod_cliente=nuevo_cliente.cod_cliente,
        direccion=nuevo_cliente.direccion,
        cod_usuario=nuevo_usuario.cod_usuario,
        apellidos=nuevo_usuario.apellidos,
        nombres=nuevo_usuario.nombres,
        correo=nuevo_usuario.correo,
        celular=nuevo_usuario.celular,
        estado=nuevo_usuario.estado
    )


@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(
    q: str = Query(None, description="Búsqueda por código o nombre"),
    estado: int = Query(None, description="Filtrar por estado del usuario (1=Activo, 0=Inactivo)"),
    skip: int = Query(0, description="Número de registros a omitir para paginación"),
    limit: int = Query(100, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """
    Listar clientes con búsqueda opcional
    """
    query = db.query(Cliente).join(Cliente.usuario)
    
    # Si hay búsqueda, filtrar
    if q:
        query = query.filter(
            or_(
                Cliente.cod_cliente.ilike(f"%{q}%"),
                Usuario.correo.ilike(f"%{q}%"),
                Usuario.apellidos.ilike(f"%{q}%"),
                Usuario.nombres.ilike(f"%{q}%")
            )
        )
    
    # Filtrar por estado si se proporciona
    if estado is not None:
        query = query.filter(Usuario.estado == estado)
    
    clientes = query.offset(skip).limit(limit).all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "cliente", 0)
    
    # Retornar con datos del usuario
    return [
        ClienteResponse(
            cod_cliente=c.cod_cliente,
            direccion=c.direccion,
            cod_usuario=c.cod_usuario,
            apellidos=c.usuario.apellidos if c.usuario else None,
            nombres=c.usuario.nombres if c.usuario else None,
            correo=c.usuario.correo if c.usuario else None,
            celular=c.usuario.celular if c.usuario else None,
            estado=c.usuario.estado if c.usuario else None
        )
        for c in clientes
    ]


@router.get("/{cod_cliente}", response_model=ClienteResponse)
def obtener_cliente(
    cod_cliente: str = Path(..., description="Código único del cliente"), 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Obtener un cliente específico con sus datos de usuario"""
    cliente = db.query(Cliente).options(joinedload(Cliente.usuario)).filter(Cliente.cod_cliente == cod_cliente).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {cod_cliente} no encontrado"
        )
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "cliente", 0)
    
    return ClienteResponse(
        cod_cliente=cliente.cod_cliente,
        direccion=cliente.direccion,
        cod_usuario=cliente.cod_usuario,
        apellidos=cliente.usuario.apellidos if cliente.usuario else None,
        nombres=cliente.usuario.nombres if cliente.usuario else None,
        correo=cliente.usuario.correo if cliente.usuario else None,
        celular=cliente.usuario.celular if cliente.usuario else None,
        estado=cliente.usuario.estado if cliente.usuario else None
    )


@router.put("/{cod_cliente}", response_model=ClienteResponse)
def actualizar_cliente(
    cliente_update: ClienteUpdate,
    cod_cliente: str = Path(..., description="Código único del cliente a actualizar"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """
    Actualizar datos de cliente y su usuario asociado
    """
    cliente = db.query(Cliente).options(joinedload(Cliente.usuario)).filter(Cliente.cod_cliente == cod_cliente).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {cod_cliente} no encontrado"
        )
    
    # Snapshot
    old_data = {
        "cod_cliente": cliente.cod_cliente,
        "direccion": cliente.direccion,
        "cod_usuario": cliente.cod_usuario,
        "apellidos": cliente.usuario.apellidos if cliente.usuario else None,
        "nombres": cliente.usuario.nombres if cliente.usuario else None,
        "correo": cliente.usuario.correo if cliente.usuario else None,
        "celular": cliente.usuario.celular if cliente.usuario else None
    }

    # Actualizar datos del cliente
    if cliente_update.direccion is not None:
        cliente.direccion = cliente_update.direccion
    
    # Actualizar datos del usuario si existen
    if cliente.usuario:
        if cliente_update.apellidos:
            cliente.usuario.apellidos = cliente_update.apellidos
        
        if cliente_update.nombres:
            cliente.usuario.nombres = cliente_update.nombres
        
        if cliente_update.correo:
            # Verificar que el correo no esté en uso por otro usuario
            existing = db.query(Usuario).filter(
                Usuario.correo == cliente_update.correo,
                Usuario.cod_usuario != cliente.usuario.cod_usuario
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El correo {cliente_update.correo} ya está en uso"
                )
            cliente.usuario.correo = cliente_update.correo
        
        if cliente_update.celular is not None:
            cliente.usuario.celular = cliente_update.celular
        
        if cliente_update.password:
            hashed_password = bcrypt.hashpw(cliente_update.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cliente.usuario.password = hashed_password
    
    # Registrar auditoría (1 = Edición)
    new_data = {
        "cod_cliente": cliente.cod_cliente,
        "direccion": cliente.direccion,
        "cod_usuario": cliente.cod_usuario,
        "apellidos": cliente.usuario.apellidos if cliente.usuario else None,
        "nombres": cliente.usuario.nombres if cliente.usuario else None,
        "correo": cliente.usuario.correo if cliente.usuario else None,
        "celular": cliente.usuario.celular if cliente.usuario else None
    }
    registrar_auditoria(db, token, "cliente", 1, old_data=old_data, new_data=new_data)
    
    db.commit()
    db.refresh(cliente)
    
    return ClienteResponse(
        cod_cliente=cliente.cod_cliente,
        direccion=cliente.direccion,
        cod_usuario=cliente.cod_usuario,
        apellidos=cliente.usuario.apellidos if cliente.usuario else None,
        nombres=cliente.usuario.nombres if cliente.usuario else None,
        correo=cliente.usuario.correo if cliente.usuario else None,
        celular=cliente.usuario.celular if cliente.usuario else None,
        estado=cliente.usuario.estado if cliente.usuario else None
    )


@router.delete("/{cod_cliente}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(
    cod_cliente: str = Path(..., description="Código único del cliente a eliminar"), 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Eliminar cliente (desactiva el usuario asociado en lugar de eliminarlo)"""
    cliente = db.query(Cliente).options(joinedload(Cliente.usuario)).filter(Cliente.cod_cliente == cod_cliente).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {cod_cliente} no encontrado"
        )
    
    # Desactivar usuario en lugar de eliminar
    if cliente.usuario:
        cliente.usuario.estado = 0
    
    # Eliminar cliente
    db.delete(cliente)
    
    # Registrar auditoría (3 = Eliminación)
    old_data = {
        "cod_cliente": cliente.cod_cliente,
        "direccion": cliente.direccion,
        "cod_usuario": cliente.cod_usuario,
        "apellidos": cliente.usuario.apellidos if cliente.usuario else None,
        "nombres": cliente.usuario.nombres if cliente.usuario else None
    }
    registrar_auditoria(db, token, "cliente", 3, old_data=old_data)
    
    db.commit()
    return None
