"""
Rutas para Artículos y Ofertas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.articulo import Articulo
from app.schemas.articulo import (
    ArticuloCreate, ArticuloUpdate, ArticuloResponse, OfertaResponse
)

router = APIRouter(
    prefix="/articulos",
    tags=["Artículos y Ofertas"],
)


@router.post("/", response_model=ArticuloResponse, status_code=status.HTTP_201_CREATED)
def crear_articulo(articulo: ArticuloCreate, db: Session = Depends(get_db)):
    """Crear nuevo artículo/oferta"""
    if db.query(Articulo).filter(Articulo.cod_articulo == articulo.cod_articulo).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Artículo {articulo.cod_articulo} ya existe"
        )
    
    nuevo_articulo = Articulo(**articulo.model_dump())
    db.add(nuevo_articulo)
    db.commit()
    db.refresh(nuevo_articulo)
    return nuevo_articulo


@router.get("/", response_model=List[ArticuloResponse])
def listar_articulos(
    skip: int = Query(0, description="Número de registros a omitir para paginación"),
    limit: int = Query(100, description="Número máximo de registros a retornar"),
    stock_min: Optional[int] = Query(None, description="Stock mínimo para filtrar artículos"),
    db: Session = Depends(get_db)
):
    """Listar todos los artículos"""
    query = db.query(Articulo)
    
    if stock_min is not None:
        query = query.filter(Articulo.stock >= stock_min)
    
    articulos = query.offset(skip).limit(limit).all()
    return articulos


@router.get("/ofertas", response_model=List[ArticuloResponse])
def ofertas_activas(db: Session = Depends(get_db)):
    """Obtener ofertas activas (artículos con stock > 0)"""
    articulos = db.query(Articulo).filter(Articulo.stock > 0).all()
    return articulos


@router.get("/search", response_model=List[ArticuloResponse])
def buscar_articulos(
    q: str = Query(..., min_length=1, description="Término de búsqueda para nombre de artículo"),
    db: Session = Depends(get_db)
):
    """Buscar artículos por nombre"""
    articulos = db.query(Articulo).filter(
        Articulo.nombre.ilike(f"%{q}%")
    ).all()
    return articulos


@router.get("/{cod_articulo}", response_model=ArticuloResponse)
def obtener_articulo(cod_articulo: int = Path(..., description="Código único del artículo"), db: Session = Depends(get_db)):
    """Obtener un artículo específico"""
    articulo = db.query(Articulo).filter(Articulo.cod_articulo == cod_articulo).first()
    if not articulo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artículo {cod_articulo} no encontrado"
        )
    return articulo


@router.put("/{cod_articulo}", response_model=ArticuloResponse)
def actualizar_articulo(
    articulo_update: ArticuloUpdate,
    cod_articulo: int = Path(..., description="Código del artículo a actualizar"),
    db: Session = Depends(get_db)
):
    """Actualizar artículo"""
    articulo = db.query(Articulo).filter(Articulo.cod_articulo == cod_articulo).first()
    if not articulo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artículo {cod_articulo} no encontrado"
        )
    
    update_data = articulo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(articulo, field, value)
    
    db.commit()
    db.refresh(articulo)
    return articulo


@router.delete("/{cod_articulo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_articulo(cod_articulo: int = Path(..., description="Código del artículo a eliminar"), db: Session = Depends(get_db)):
    """Eliminar artículo/oferta (baja)"""
    articulo = db.query(Articulo).filter(Articulo.cod_articulo == cod_articulo).first()
    if not articulo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artículo {cod_articulo} no encontrado"
        )
    
    db.delete(articulo)
    db.commit()
    return None


@router.patch("/{cod_articulo}/stock")
def actualizar_stock(
    cod_articulo: int = Path(..., description="Código del artículo para actualizar stock"),
    cantidad: int = Query(..., description="Nueva cantidad de stock"),
    db: Session = Depends(get_db)
):
    """Actualizar stock de un artículo"""
    articulo = db.query(Articulo).filter(Articulo.cod_articulo == cod_articulo).first()
    if not articulo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artículo {cod_articulo} no encontrado"
        )
    
    articulo.stock = cantidad
    db.commit()
    
    return {"message": f"Stock actualizado a {cantidad}"}
