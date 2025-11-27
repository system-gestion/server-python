"""
Rutas CRUD para Pedidos
Gestión completa de pedidos con filtros y estados
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.pedido import Pedido
from app.models.cliente import Cliente
from app.models.detalle_pedido import DetallePedido
from app.models.articulo import Articulo
from app.schemas.pedido import (
    PedidoCreate, PedidoUpdate, PedidoResponse,
    DetallePedidoCreate, DetallePedidoResponse, PedidoEstadistica
)
from app.core.security import registrar_auditoria, get_token

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"],
)


@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    pedido: PedidoCreate, 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Crear nuevo pedido con detalles"""
    # Verificar cliente existe
    cliente = db.query(Cliente).filter(Cliente.cod_cliente == pedido.cod_cliente).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {pedido.cod_cliente} no encontrado"
        )
    
    # Crear pedido
    pedido_data = pedido.model_dump(exclude={'detalles'})
    nuevo_pedido = Pedido(**pedido_data)
    db.add(nuevo_pedido)
    db.flush()
    
    # Agregar detalles
    if pedido.detalles:
        for detalle in pedido.detalles:
            # Verificar artículo existe
            articulo = db.query(Articulo).filter(
                Articulo.cod_articulo == detalle.cod_articulo
            ).first()
            if not articulo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Artículo {detalle.cod_articulo} no encontrado"
                )
            
            nuevo_detalle = DetallePedido(
                num_pedido=nuevo_pedido.num_pedido,
                **detalle.model_dump()
            )
            db.add(nuevo_detalle)
    
    # Registrar auditoría (2 = Inserción)
    registrar_auditoria(db, token, "pedido", 2, datos={"num_pedido": nuevo_pedido.num_pedido})
    
    db.commit()
    db.refresh(nuevo_pedido)
    
    # Cargar relaciones
    pedido_response = db.query(Pedido).options(
        joinedload(Pedido.cliente),
        joinedload(Pedido.detalles).joinedload(DetallePedido.articulo)
    ).filter(Pedido.num_pedido == nuevo_pedido.num_pedido).first()
    
    return _format_pedido_response(pedido_response)


@router.get("/", response_model=List[PedidoResponse])
def listar_pedidos(
    skip: int = Query(0, description="Número de registros a omitir para paginación"),
    limit: int = Query(100, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Listar todos los pedidos"""
    pedidos = db.query(Pedido).options(
        joinedload(Pedido.cliente),
        joinedload(Pedido.detalles).joinedload(DetallePedido.articulo)
    ).offset(skip).limit(limit).all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "pedido", 0)
    
    return [_format_pedido_response(p) for p in pedidos]


@router.get("/search", response_model=List[PedidoResponse])
def buscar_pedidos(
    cod_cliente: Optional[str] = Query(None, description="Código del cliente para filtrar pedidos"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicial del rango de búsqueda"),
    fecha_fin: Optional[date] = Query(None, description="Fecha final del rango de búsqueda"),
    importe_min: Optional[float] = Query(None, description="Importe mínimo del pedido"),
    importe_max: Optional[float] = Query(None, description="Importe máximo del pedido"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Buscar pedidos con múltiples filtros"""
    query = db.query(Pedido).options(
        joinedload(Pedido.cliente),
        joinedload(Pedido.detalles).joinedload(DetallePedido.articulo)
    )
    
    if cod_cliente:
        query = query.filter(Pedido.cod_cliente == cod_cliente)
    if fecha_inicio:
        query = query.filter(Pedido.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Pedido.fecha <= fecha_fin)
    if importe_min is not None:
        query = query.filter(Pedido.importe >= importe_min)
    if importe_max is not None:
        query = query.filter(Pedido.importe <= importe_max)
    
    pedidos = query.all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "pedido", 0)
    
    return [_format_pedido_response(p) for p in pedidos]


@router.get("/by-date", response_model=List[PedidoResponse])
def pedidos_por_fecha(
    fecha: date = Query(..., description="Fecha específica para filtrar pedidos"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Obtener pedidos de una fecha específica"""
    pedidos = db.query(Pedido).options(
        joinedload(Pedido.cliente),
        joinedload(Pedido.detalles).joinedload(DetallePedido.articulo)
    ).filter(Pedido.fecha == fecha).all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "pedido", 0)
    
    return [_format_pedido_response(p) for p in pedidos]


@router.get("/by-number/{num_pedido}", response_model=PedidoResponse)
def pedido_por_numero(
    num_pedido: int = Path(..., description="Número único del pedido"), 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Obtener pedido por número"""
    pedido = db.query(Pedido).options(
        joinedload(Pedido.cliente),
        joinedload(Pedido.detalles).joinedload(DetallePedido.articulo)
    ).filter(Pedido.num_pedido == num_pedido).first()
    
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido {num_pedido} no encontrado"
        )
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "pedido", 0)
    
    return _format_pedido_response(pedido)


@router.get("/pending", response_model=List[PedidoResponse])
def pedidos_pendientes(
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Pedidos pendientes de entrega (estado = 1)"""
    pedidos = db.query(Pedido).options(
        joinedload(Pedido.cliente),
        joinedload(Pedido.detalles).joinedload(DetallePedido.articulo)
    ).filter(
        Pedido.estado == 1  # 1 = pending
    ).all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "pedido", 0)
    
    return [_format_pedido_response(p) for p in pedidos]


@router.get("/completed", response_model=List[PedidoResponse])
def pedidos_completados(
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Pedidos completados (estado = 2)"""
    pedidos = db.query(Pedido).options(
        joinedload(Pedido.cliente),
        joinedload(Pedido.detalles).joinedload(DetallePedido.articulo)
    ).filter(
        Pedido.estado == 2  # 2 = completed
    ).all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "pedido", 0)
    
    return [_format_pedido_response(p) for p in pedidos]


@router.get("/cancelled", response_model=List[PedidoResponse])
def pedidos_cancelados(
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Pedidos cancelados (estado = 3)"""
    pedidos = db.query(Pedido).options(
        joinedload(Pedido.cliente),
        joinedload(Pedido.detalles).joinedload(DetallePedido.articulo)
    ).filter(
        Pedido.estado == 3  # 3 = cancelled
    ).all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "pedido", 0)
    
    return [_format_pedido_response(p) for p in pedidos]


@router.get("/cliente/{cod_cliente}", response_model=List[PedidoResponse])
def pedidos_de_cliente(
    cod_cliente: str = Path(..., description="Código del cliente para obtener sus pedidos"), 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Obtener todos los pedidos de un cliente específico"""
    pedidos = db.query(Pedido).options(
        joinedload(Pedido.cliente),
        joinedload(Pedido.detalles).joinedload(DetallePedido.articulo)
    ).filter(Pedido.cod_cliente == cod_cliente).all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "pedido", 0)
    
    return [_format_pedido_response(p) for p in pedidos]


@router.get("/estadisticas", response_model=PedidoEstadistica)
def estadisticas_pedidos(
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicial para el cálculo de estadísticas"),
    fecha_fin: Optional[date] = Query(None, description="Fecha final para el cálculo de estadísticas"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Obtener estadísticas generales de pedidos"""
    query = db.query(Pedido)
    
    if fecha_inicio:
        query = query.filter(Pedido.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Pedido.fecha <= fecha_fin)
    
    total = query.count()
    importe_total = db.query(func.sum(Pedido.importe)).scalar() or 0
    promedio = importe_total / total if total > 0 else 0
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "pedido", 0)
    
    return {
        "total_pedidos": total,
        "importe_total": float(importe_total),
        "promedio": float(promedio),
        "pendientes": 0,  # Implementar según tu lógica
        "completados": total,
        "cancelados": 0
    }


@router.put("/{num_pedido}", response_model=PedidoResponse)
def actualizar_pedido(
    pedido_update: PedidoUpdate,
    num_pedido: int = Path(..., description="Número del pedido a actualizar"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Actualizar datos de un pedido"""
    pedido = db.query(Pedido).filter(Pedido.num_pedido == num_pedido).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido {num_pedido} no encontrado"
        )
    
    update_data = pedido_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pedido, field, value)
    
    # Registrar auditoría (1 = Edición)
    original_data = {
        "num_pedido": pedido.num_pedido,
        "cod_cliente": pedido.cod_cliente,
        "fecha": str(pedido.fecha),
        "fecha_entrega": str(pedido.fecha_entrega) if pedido.fecha_entrega else None,
        "importe": float(pedido.importe),
        "estado": pedido.estado,
        "observaciones": pedido.observaciones
    }
    registrar_auditoria(db, token, "pedido", 1, datos=original_data)
    
    db.commit()
    db.refresh(pedido)
    
    pedido_response = db.query(Pedido).options(
        joinedload(Pedido.cliente),
        joinedload(Pedido.detalles).joinedload(DetallePedido.articulo)
    ).filter(Pedido.num_pedido == num_pedido).first()
    
    return _format_pedido_response(pedido_response)


@router.patch("/{num_pedido}/cancel")
def anular_pedido(
    num_pedido: int = Path(..., description="Número del pedido a anular"), 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Anular un pedido (marcar detalles como quitados y cambiar estado a 3=cancelled)"""
    pedido = db.query(Pedido).filter(Pedido.num_pedido == num_pedido).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido {num_pedido} no encontrado"
        )
    
    # Capture previous state
    estado_anterior = pedido.estado

    # Cambiar estado del pedido a cancelado (3)
    pedido.estado = 3  # 3 = cancelled
    
    # Marcar todos los detalles como quitados
    db.query(DetallePedido).filter(
        DetallePedido.num_pedido == num_pedido
    ).update({"estado": 0})
    
    # Registrar auditoría (1 = Edición)
    original_data = {
        "num_pedido": pedido.num_pedido,
        "estado": estado_anterior,
        "was_cancelled": False
    }
    registrar_auditoria(db, token, "pedido", 1, datos=original_data)
    
    db.commit()
    
    return {"message": f"Pedido {num_pedido} anulado exitosamente"}


@router.delete("/{num_pedido}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pedido(
    num_pedido: int = Path(..., description="Número del pedido a eliminar"), 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Eliminar pedido permanentemente"""
    pedido = db.query(Pedido).filter(Pedido.num_pedido == num_pedido).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido {num_pedido} no encontrado"
        )
    
    db.delete(pedido)
    
    # Registrar auditoría (3 = Eliminación)
    full_data = _format_pedido_response(pedido)
    # Convertir objetos date a string para JSON
    full_data["fecha"] = str(full_data["fecha"])
    if full_data.get("fecha_entrega"):
        full_data["fecha_entrega"] = str(full_data["fecha_entrega"])
        
    registrar_auditoria(db, token, "pedido", 3, datos=full_data)
    
    db.commit()
    return None


def _format_pedido_response(pedido: Pedido) -> dict:
    """Helper para formatear respuesta de pedido con nombres"""
    return {
        **PedidoResponse.model_validate(pedido).model_dump(),
        "nombre_cliente": pedido.cliente.nombre if pedido.cliente else None,
        "detalles": [
            {
                **DetallePedidoResponse.model_validate(d).model_dump(),
                "nombre_articulo": d.articulo.nombre if d.articulo else None,
                "pvp": d.articulo.pvp if d.articulo else None
            }
            for d in pedido.detalles
        ]
    }
