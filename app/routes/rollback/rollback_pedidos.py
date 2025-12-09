from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from app.models.pedido import Pedido
from app.models.detalle_pedido import DetallePedido

def rollback_pedido(db: Session, accion: int, datos: dict) -> str:
    """
    Lógica de rollback para la tabla 'pedido'
    """
    # Rollback Inserción (2)
    if accion == 2:
        num_pedido = datos.get("num_pedido")
        if not num_pedido:
            raise HTTPException(status_code=400, detail="Snapshot incompleto (falta ID)")
        
        pedido = db.query(Pedido).filter(Pedido.num_pedido == num_pedido).first()
        if pedido:
            db.delete(pedido)
            return f"Rollback: Pedido {num_pedido} eliminado (reversión de inserción)"
        else:
            return f"Rollback: Pedido {num_pedido} ya no existe"

    # Rollback Edición (1)
    elif accion == 1:
        num_pedido = datos.get("num_pedido")
        pedido = db.query(Pedido).filter(Pedido.num_pedido == num_pedido).first()
        
        if not pedido:
            raise HTTPException(status_code=400, detail="Pedido no encontrado para rollback")

        # Restore fields
        for key, value in datos.items():
            if hasattr(pedido, key) and key != "num_pedido" and key != "was_cancelled":
                # Convert date strings back to date objects if needed
                if key in ["fecha", "fecha_entrega"] and isinstance(value, str):
                    try:
                        value = datetime.strptime(value, "%Y-%m-%d").date()
                    except ValueError:
                        pass # Keep as string if format fails, let SQLAlchemy handle or fail
                setattr(pedido, key, value)
        
        # Special handling for un-cancelling
        if pedido.estado != 3:
                db.query(DetallePedido).filter(DetallePedido.num_pedido == num_pedido).update({"estado": 1})

        return f"Rollback: Pedido {num_pedido} restaurado a estado previo"

    # Rollback Eliminación (3)
    elif accion == 3:
        pedido_data = datos.copy()
        detalles_data = pedido_data.pop("detalles", [])
        
        # Remove extra fields
        pedido_data.pop("nombre_cliente", None)
        pedido_data.pop("nombre_vendedor", None)
        
        # Convert dates
        if "fecha" in pedido_data and isinstance(pedido_data["fecha"], str):
                pedido_data["fecha"] = datetime.strptime(pedido_data["fecha"], "%Y-%m-%d").date()
        if "fecha_entrega" in pedido_data and isinstance(pedido_data["fecha_entrega"], str):
                pedido_data["fecha_entrega"] = datetime.strptime(pedido_data["fecha_entrega"], "%Y-%m-%d").date()

        # Create Pedido
        nuevo_pedido = Pedido(**pedido_data)
        db.add(nuevo_pedido)
        db.flush() 
        
        # Create Detalles
        for d_data in detalles_data:
            d_data.pop("nombre_articulo", None)
            d_data.pop("pvp", None)
            nuevo_detalle = DetallePedido(**d_data)
            db.add(nuevo_detalle)
            
        return f"Rollback: Pedido {datos.get('num_pedido')} restaurado (reversión de eliminación)"
        
    else:
            raise HTTPException(status_code=400, detail=f"Acción {accion} no soportada")
