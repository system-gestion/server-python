from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.articulo import Articulo

def rollback_oferta(db: Session, accion: int, datos: dict) -> str:
    """
    Lógica de rollback para la tabla 'oferta' (que en realidad modifica 'articulo')
    """
    cod_articulo = datos.get("cod_articulo")
    if not cod_articulo:
        raise HTTPException(status_code=400, detail="Snapshot incompleto (falta ID de artículo)")

    articulo = db.query(Articulo).filter(Articulo.cod_articulo == cod_articulo).first()
    if not articulo:
         return f"Rollback: Artículo {cod_articulo} no encontrado, no se puede restaurar la oferta"

    # Rollback de Inserción (2) -> "Eliminar" oferta (poner descuento a 0)
    if accion == 2:
        articulo.tipo_descuento = 0
        articulo.valor_descuento = 0.0
        return f"Rollback: Oferta eliminada para artículo {cod_articulo} (reversión de creación)"

    # Rollback de Edición (1) -> Restaurar valores previos
    elif accion == 1:
        if "tipo_descuento" in datos:
            articulo.tipo_descuento = datos["tipo_descuento"]
        if "valor_descuento" in datos:
            articulo.valor_descuento = datos["valor_descuento"]
            
        return f"Rollback: Oferta restaurada para artículo {cod_articulo}"

    # Rollback de Eliminación (3) -> Restaurar oferta eliminada
    elif accion == 3:
        if "tipo_descuento" in datos:
            articulo.tipo_descuento = datos["tipo_descuento"]
        if "valor_descuento" in datos:
            articulo.valor_descuento = datos["valor_descuento"]
            
        return f"Rollback: Oferta recuperada para artículo {cod_articulo} (reversión de eliminación)"
            
    else:
        raise HTTPException(status_code=400, detail=f"Acción {accion} no soportada para rollback de ofertas")
