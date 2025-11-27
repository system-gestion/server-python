"""
Rutas para Artículos y Ofertas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.articulo import Articulo
from app.schemas.articulo import (
    ArticuloCreate, ArticuloUpdate, ArticuloResponse
)
from app.core.security import registrar_auditoria, get_token

router = APIRouter(
    prefix="/articulos",
    tags=["Artículos y Ofertas"],
)


@router.post("/", response_model=ArticuloResponse, status_code=status.HTTP_201_CREATED)
def crear_articulo(
    articulo: ArticuloCreate, 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Crear nuevo artículo/oferta"""
    if db.query(Articulo).filter(Articulo.cod_articulo == articulo.cod_articulo).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Artículo {articulo.cod_articulo} ya existe"
        )
    
    nuevo_articulo = Articulo(**articulo.model_dump())
    db.add(nuevo_articulo)
    
    # Registrar auditoría (2 = Inserción)
    registrar_auditoria(db, token, "articulo", 2, new_data=articulo.model_dump())
    
    db.commit()
    db.refresh(nuevo_articulo)
    return nuevo_articulo


@router.get("/", response_model=List[ArticuloResponse])
def listar_articulos(
    skip: int = Query(0, description="Número de registros a omitir para paginación"),
    limit: int = Query(100, description="Número máximo de registros a retornar"),
    stock_min: Optional[int] = Query(None, description="Stock mínimo para filtrar artículos"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Listar todos los artículos"""
    query = db.query(Articulo)
    
    if stock_min is not None:
        query = query.filter(Articulo.stock >= stock_min)
    
    articulos = query.offset(skip).limit(limit).all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "articulo", 0)
    
    return articulos


@router.get("/search", response_model=List[ArticuloResponse])
def buscar_articulos(
    q: str = Query(..., min_length=1, description="Término de búsqueda para nombre de artículo"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Buscar artículos por nombre"""
    articulos = db.query(Articulo).filter(
        Articulo.nombre.ilike(f"%{q}%")
    ).all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "articulo", 0)
    
    return articulos


@router.get("/{cod_articulo}", response_model=ArticuloResponse)
def obtener_articulo(
    cod_articulo: int = Path(..., description="Código único del artículo"), 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Obtener un artículo específico"""
    articulo = db.query(Articulo).filter(Articulo.cod_articulo == cod_articulo).first()
    if not articulo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artículo {cod_articulo} no encontrado"
        )
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "articulo", 0)
    
    return articulo


@router.put("/{cod_articulo}", response_model=ArticuloResponse)
def actualizar_articulo(
    articulo_update: ArticuloUpdate,
    cod_articulo: int = Path(..., description="Código del artículo a actualizar"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Actualizar artículo"""
    articulo = db.query(Articulo).filter(Articulo.cod_articulo == cod_articulo).first()
    if not articulo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artículo {cod_articulo} no encontrado"
        )
    
    # Snapshot
    old_data = {
        "cod_articulo": articulo.cod_articulo,
        "nombre": articulo.nombre,
        "pvp": float(articulo.pvp),
        "stock": articulo.stock,
        "tipo_descuento": articulo.tipo_descuento,
        "valor_descuento": float(articulo.valor_descuento) if articulo.valor_descuento else None
    }

    update_data = articulo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(articulo, field, value)
    
    # Registrar auditoría (1 = Edición)
    new_data = old_data.copy()
    new_data.update(update_data)
    registrar_auditoria(db, token, "articulo", 1, old_data=old_data, new_data=new_data)
    
    db.commit()
    db.refresh(articulo)
    return articulo


@router.delete("/{cod_articulo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_articulo(
    cod_articulo: int = Path(..., description="Código del artículo a eliminar"), 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Eliminar artículo/oferta (baja)"""
    articulo = db.query(Articulo).filter(Articulo.cod_articulo == cod_articulo).first()
    if not articulo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artículo {cod_articulo} no encontrado"
        )
    
    db.delete(articulo)
    
    # Registrar auditoría (3 = Eliminación)
    old_data = {
        "cod_articulo": articulo.cod_articulo,
        "nombre": articulo.nombre,
        "pvp": articulo.pvp,
        "stock": articulo.stock
    }
    registrar_auditoria(db, token, "articulo", 3, old_data=old_data)
    
    db.commit()
    return None


@router.patch("/{cod_articulo}/stock")
def actualizar_stock(
    cod_articulo: int = Path(..., description="Código del artículo para actualizar stock"),
    cantidad: int = Query(..., description="Nueva cantidad de stock"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Actualizar stock de un artículo"""
    articulo = db.query(Articulo).filter(Articulo.cod_articulo == cod_articulo).first()
    if not articulo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artículo {cod_articulo} no encontrado"
        )
    
    # Snapshot
    old_data = {
        "cod_articulo": articulo.cod_articulo,
        "nombre": articulo.nombre,
        "pvp": float(articulo.pvp),
        "stock": articulo.stock,
        "tipo_descuento": articulo.tipo_descuento,
        "valor_descuento": float(articulo.valor_descuento) if articulo.valor_descuento else None
    }

    articulo.stock = cantidad
    
    # Registrar auditoría (1 = Edición)
    new_data = old_data.copy()
    new_data["stock"] = cantidad
    registrar_auditoria(db, token, "articulo", 1, old_data=old_data, new_data=new_data)
    
    db.commit()
    
    return {"message": f"Stock actualizado a {cantidad}"}
