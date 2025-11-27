from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.articulo import Articulo
from app.schemas.oferta import OfertaResponse, OfertaCreate, OfertaUpdate
from app.core.security import registrar_auditoria, get_token

router = APIRouter(
    prefix="/ofertas",
    tags=["Ofertas"]
)

@router.get("/", response_model=List[OfertaResponse])
def listar_ofertas(
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Listar todas las ofertas activas (artículos con descuento)"""
    ofertas = db.query(Articulo).filter(Articulo.tipo_descuento > 0).all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "oferta", 0)
    
    return ofertas

@router.post("/", response_model=OfertaResponse)
def crear_oferta(
    oferta: OfertaCreate, 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Crear una oferta (asignar descuento a un artículo)"""
    articulo = db.query(Articulo).filter(Articulo.cod_articulo == oferta.cod_articulo).first()
    if not articulo:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    
    articulo.tipo_descuento = oferta.tipo_descuento
    articulo.valor_descuento = oferta.valor_descuento
    
    # Registrar auditoría (2 = Inserción - aunque es update en tabla articulo, conceptualmente es crear oferta)
    registrar_auditoria(db, token, "oferta", 2)
    
    db.commit()
    db.refresh(articulo)
    return articulo

@router.put("/{cod_articulo}", response_model=OfertaResponse)
def actualizar_oferta(
    oferta_update: OfertaUpdate,
    cod_articulo: int = Path(..., description="Código del artículo"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Actualizar una oferta existente"""
    articulo = db.query(Articulo).filter(Articulo.cod_articulo == cod_articulo).first()
    if not articulo:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
        
    if oferta_update.tipo_descuento is not None:
        articulo.tipo_descuento = oferta_update.tipo_descuento
    if oferta_update.valor_descuento is not None:
        articulo.valor_descuento = oferta_update.valor_descuento
        
    # Registrar auditoría (1 = Edición)
    registrar_auditoria(db, token, "oferta", 1)
        
    db.commit()
    db.refresh(articulo)
    return articulo

@router.delete("/{cod_articulo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_oferta(
    cod_articulo: int, 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Eliminar una oferta (quitar descuento)"""
    articulo = db.query(Articulo).filter(Articulo.cod_articulo == cod_articulo).first()
    if not articulo:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    
    articulo.tipo_descuento = 0
    articulo.valor_descuento = 0.0
    
    # Registrar auditoría (3 = Eliminación)
    registrar_auditoria(db, token, "oferta", 3)
    
    db.commit()
    return None
