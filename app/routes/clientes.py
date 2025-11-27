"""
Rutas CRUD para Clientes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from app.database import get_db
from app.models.cliente import Cliente
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
    """Crear nuevo cliente"""
    if db.query(Cliente).filter(Cliente.cod_cliente == cliente.cod_cliente).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cliente {cliente.cod_cliente} ya existe"
        )
    
    nuevo_cliente = Cliente(**cliente.model_dump())
    db.add(nuevo_cliente)
    
    # Registrar auditoría (2 = Inserción)
    registrar_auditoria(db, token, "cliente", 2)
    
    db.commit()
    db.refresh(nuevo_cliente)
    return nuevo_cliente


@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(
    skip: int = Query(0, description="Número de registros a omitir para paginación"),
    limit: int = Query(100, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Listar todos los clientes"""
    clientes = db.query(Cliente).offset(skip).limit(limit).all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "cliente", 0)
    
    return clientes


@router.get("/search", response_model=List[ClienteResponse])
def buscar_clientes(
    q: str = Query(..., min_length=1, description="Término de búsqueda para nombre o código de cliente"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Buscar clientes por nombre o código"""
    clientes = db.query(Cliente).filter(
        or_(
            Cliente.nombre.ilike(f"%{q}%"),
            Cliente.cod_cliente.ilike(f"%{q}%")
        )
    ).all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "cliente", 0)
    
    return clientes


@router.get("/{cod_cliente}", response_model=ClienteResponse)
def obtener_cliente(
    cod_cliente: str = Path(..., description="Código único del cliente"), 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Obtener un cliente específico"""
    cliente = db.query(Cliente).filter(Cliente.cod_cliente == cod_cliente).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {cod_cliente} no encontrado"
        )
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "cliente", 0)
    
    return cliente


@router.put("/{cod_cliente}", response_model=ClienteResponse)
def actualizar_cliente(
    cliente_update: ClienteUpdate,
    cod_cliente: str = Path(..., description="Código único del cliente a actualizar"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Actualizar datos de cliente"""
    cliente = db.query(Cliente).filter(Cliente.cod_cliente == cod_cliente).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {cod_cliente} no encontrado"
        )
    
    update_data = cliente_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cliente, field, value)
    
    # Registrar auditoría (1 = Edición)
    registrar_auditoria(db, token, "cliente", 1)
    
    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/{cod_cliente}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(
    cod_cliente: str = Path(..., description="Código único del cliente a eliminar"), 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Eliminar cliente"""
    cliente = db.query(Cliente).filter(Cliente.cod_cliente == cod_cliente).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {cod_cliente} no encontrado"
        )
    
    db.delete(cliente)
    
    # Registrar auditoría (3 = Eliminación)
    registrar_auditoria(db, token, "cliente", 3)
    
    db.commit()
    return None
