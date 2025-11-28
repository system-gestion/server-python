from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websockets.connection_manager import manager

router = APIRouter()

@router.websocket("/ws/users/editing")
async def websocket_endpoint(websocket: WebSocket, supervisor_name: str = Query(...)):
    """
    Endpoint WebSocket para gestionar bloqueos de edición de usuarios.
    Requiere el nombre del supervisor como query param.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Formato esperado: "LOCK {user_id}" o "UNLOCK {user_id}"
            parts = data.split(" ")
            command = parts[0]
            
            if len(parts) < 2:
                continue
                
            try:
                user_id = int(parts[1])
            except ValueError:
                continue

            if command == "LOCK":
                success = await manager.request_lock(websocket, user_id, supervisor_name)
                if success:
                    await websocket.send_text(f"GRANTED {user_id}")
                else:
                    owner = manager.get_lock_owner(user_id)
                    await websocket.send_text(f"LOCKED {user_id} BY {owner}")
            
            elif command == "UNLOCK":
                await manager.release_lock(websocket, user_id)
                # Opcional: Notificar a otros que se liberó (no estrictamente necesario para este req)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
