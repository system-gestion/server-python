"""
Rutas para cálculo de comisiones de vendedores
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List
from datetime import date, timedelta

from app.database import get_db
from app.models.usuario import Usuario
from app.models.pedido import Pedido
from app.models.cliente import Cliente
from app.schemas.comision import ComisionResponse, ComisionDetalle
from app.core.security import registrar_auditoria, get_token

router = APIRouter(
    prefix="/comisiones",
    tags=["Comisiones"],
)


@router.get("/vendedor/{cod_usuario}", response_model=ComisionResponse)
def calcular_comision_vendedor(
    cod_usuario: int = Path(..., description="Código del vendedor para calcular comisiones"),
    fecha_inicio: date = Query(default_factory=lambda: date.today() - timedelta(days=30), description="Fecha inicial del período de cálculo"),
    fecha_fin: date = Query(default_factory=date.today, description="Fecha final del período de cálculo"),
    porcentaje: float = Query(default=5.0, ge=0, le=100, description="Porcentaje de comisión a aplicar"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Calcular comisiones de un vendedor en un período"""
    # Verificar que el usuario es vendedor
    usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {cod_usuario} no encontrado"
        )
    
    if usuario.nivel != 2:  # 2 = vendedor
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no es un vendedor"
        )
    
    # Calcular ventas del período
    # Asumiendo que el vendedor está asociado al cliente
    # En producción necesitarías una relación explícita vendedor-pedido
    
    pedidos = db.query(Pedido).filter(
        and_(
            Pedido.fecha >= fecha_inicio,
            Pedido.fecha <= fecha_fin
        )
    ).all()
    
    total_ventas = sum(p.importe for p in pedidos)
    cantidad_pedidos = len(pedidos)
    comision_total = total_ventas * (porcentaje / 100)
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "comision", 0)
    
    return {
        "cod_usuario": usuario.cod_usuario,
        "nombre_vendedor": f"{usuario.nombres} {usuario.apellidos}",
        "total_ventas": total_ventas,
        "cantidad_pedidos": cantidad_pedidos,
        "porcentaje_comision": porcentaje,
        "comision_total": comision_total,
        "periodo_inicio": fecha_inicio,
        "periodo_fin": fecha_fin
    }


@router.get("/vendedor/{cod_usuario}/detalles", response_model=List[ComisionDetalle])
def detalle_comisiones_vendedor(
    cod_usuario: int = Path(..., description="Código del vendedor para obtener detalle de comisiones"),
    fecha_inicio: date = Query(default_factory=lambda: date.today() - timedelta(days=30), description="Fecha inicial del período de detalle"),
    fecha_fin: date = Query(default_factory=date.today, description="Fecha final del período de detalle"),
    porcentaje: float = Query(default=5.0, ge=0, le=100, description="Porcentaje de comisión a aplicar"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Obtener detalle de cada pedido para comisiones"""
    usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {cod_usuario} no encontrado"
        )
    
    pedidos = db.query(Pedido).filter(
        and_(
            Pedido.fecha >= fecha_inicio,
            Pedido.fecha <= fecha_fin
        )
    ).all()
    
    detalles = []
    for pedido in pedidos:
        cliente = db.query(Cliente).filter(
            Cliente.cod_cliente == pedido.cod_cliente
        ).first()
        
        detalles.append({
            "num_pedido": pedido.num_pedido,
            "fecha": pedido.fecha,
            "cod_cliente": pedido.cod_cliente,
            "nombre_cliente": cliente.usuario.nombres + " " + cliente.usuario.apellidos if cliente else None,
            "importe": pedido.importe,
            "comision": pedido.importe * (porcentaje / 100)
        })
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "comision", 0)
    
    return detalles


@router.get("/resumen", response_model=List[ComisionResponse])
def resumen_comisiones_todos(
    fecha_inicio: date = Query(default_factory=lambda: date.today() - timedelta(days=30), description="Fecha inicial del período de resumen"),
    fecha_fin: date = Query(default_factory=date.today, description="Fecha final del período de resumen"),
    porcentaje: float = Query(default=5.0, ge=0, le=100, description="Porcentaje de comisión a aplicar"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Resumen de comisiones de todos los vendedores"""
    vendedores = db.query(Usuario).filter(Usuario.nivel == 2, Usuario.estado == 1).all()
    
    resultado = []
    for vendedor in vendedores:
        pedidos = db.query(Pedido).filter(
            and_(
                Pedido.fecha >= fecha_inicio,
                Pedido.fecha <= fecha_fin
            )
        ).all()
        
        total_ventas = sum(p.importe for p in pedidos)
        cantidad_pedidos = len(pedidos)
        comision_total = total_ventas * (porcentaje / 100)
        
        resultado.append({
            "cod_usuario": vendedor.cod_usuario,
            "nombre_vendedor": f"{vendedor.nombres} {vendedor.apellidos}",
            "total_ventas": total_ventas,
            "cantidad_pedidos": cantidad_pedidos,
            "porcentaje_comision": porcentaje,
            "comision_total": comision_total,
            "periodo_inicio": fecha_inicio,
            "periodo_fin": fecha_fin
        })
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "comision", 0)
    
    return resultado
