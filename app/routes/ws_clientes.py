from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websockets.connection_manager import manager

router = APIRouter()

@router.websocket("/ws/clientes/editing")
async def websocket_endpoint(websocket: WebSocket, vendedor_name: str = Query(...)):
    """
    Endpoint WebSocket para gestionar bloqueos de edición de clientes.
    Requiere el nombre del vendedor/supervisor como query param.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Formato esperado: "LOCK {cliente_id}" o "UNLOCK {cliente_id}"
            parts = data.split(" ", 1)  # Split en máximo 2 partes
            command = parts[0]
            
            if len(parts) < 2:
                continue
                
            cliente_id = parts[1]  # Mantener como string (ej: "CLI001")

            if command == "LOCK":
                success = await manager.request_client_lock(websocket, cliente_id, vendedor_name)
                if success:
                    await websocket.send_text(f"GRANTED {cliente_id}")
                else:
                    owner = manager.get_client_lock_owner(cliente_id)
                    await websocket.send_text(f"LOCKED {cliente_id} BY {owner}")
            
            elif command == "UNLOCK":
                await manager.release_client_lock(websocket, cliente_id)
                # Opcional: Notificar a otros que se liberó (no estrictamente necesario para este req)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
