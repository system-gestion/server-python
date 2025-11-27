from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.articulo import Articulo
from app.schemas.oferta import OfertaResponse, OfertaCreate, OfertaUpdate

router = APIRouter(
    prefix="/ofertas",
    tags=["Ofertas"]
)

@router.get("/", response_model=List[OfertaResponse])
def listar_ofertas(db: Session = Depends(get_db)):
    """Listar todas las ofertas activas (artículos con descuento)"""
    return db.query(Articulo).filter(Articulo.tipo_descuento > 0).all()

@router.post("/", response_model=OfertaResponse)
def crear_oferta(oferta: OfertaCreate, db: Session = Depends(get_db)):
    """Crear una oferta (asignar descuento a un artículo)"""
    articulo = db.query(Articulo).filter(Articulo.cod_articulo == oferta.cod_articulo).first()
    if not articulo:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    
    articulo.tipo_descuento = oferta.tipo_descuento
    articulo.valor_descuento = oferta.valor_descuento
    db.commit()
    db.refresh(articulo)
    return articulo

@router.put("/{cod_articulo}", response_model=OfertaResponse)
def actualizar_oferta(
    oferta_update: OfertaUpdate,
    cod_articulo: int = Path(..., description="Código del artículo"),
    db: Session = Depends(get_db)
):
    """Actualizar una oferta existente"""
    articulo = db.query(Articulo).filter(Articulo.cod_articulo == cod_articulo).first()
    if not articulo:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
        
    if oferta_update.tipo_descuento is not None:
        articulo.tipo_descuento = oferta_update.tipo_descuento
    if oferta_update.valor_descuento is not None:
        articulo.valor_descuento = oferta_update.valor_descuento
        
    db.commit()
    db.refresh(articulo)
    return articulo

@router.delete("/{cod_articulo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_oferta(cod_articulo: int, db: Session = Depends(get_db)):
    """Eliminar una oferta (quitar descuento)"""
    articulo = db.query(Articulo).filter(Articulo.cod_articulo == cod_articulo).first()
    if not articulo:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    
    articulo.tipo_descuento = 0
    articulo.valor_descuento = 0.0
    db.commit()
    return None
