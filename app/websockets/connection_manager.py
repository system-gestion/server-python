from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Mantiene las conexiones activas: {supervisor_id: WebSocket}
        self.active_connections: List[WebSocket] = []
        
        # Mantiene los bloqueos: {user_id_to_edit: {'socket': WebSocket, 'name': str}}
        self.active_locks: Dict[int, dict] = {}
        
        # Mapeo inverso para saber qué locks tiene un socket (para limpieza)
        # {websocket: [user_id_locked]}
        self.socket_locks: Dict[WebSocket, List[int]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.socket_locks[websocket] = []

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Liberar locks asociados a este socket
        if websocket in self.socket_locks:
            for user_id in self.socket_locks[websocket]:
                if user_id in self.active_locks:
                    # Verificar que el lock realmente pertenece a este socket antes de borrar
                    # (aunque socket_locks debería estar sincronizado)
                    if self.active_locks[user_id]['socket'] == websocket:
                        del self.active_locks[user_id]
            del self.socket_locks[websocket]

    async def request_lock(self, websocket: WebSocket, user_id: int, supervisor_name: str) -> bool:
        """
        Intenta adquirir un lock para editar un usuario.
        Retorna True si se otorga, False si ya está bloqueado por otro socket.
        """
        if user_id in self.active_locks:
            current_lock = self.active_locks[user_id]
            # Si el lock pertenece al MISMO socket, permitimos (idempotencia)
            if current_lock['socket'] == websocket:
                return True
            # Si es otro socket, denegamos (incluso si es el mismo usuario en otra pestaña)
            return False
        
        # Otorgar lock
        self.active_locks[user_id] = {'socket': websocket, 'name': supervisor_name}
        if websocket in self.socket_locks:
            self.socket_locks[websocket].append(user_id)
        return True

    async def release_lock(self, websocket: WebSocket, user_id: int):
        """
        Libera el lock de un usuario si pertenece al socket solicitante.
        """
        if user_id in self.active_locks:
            if self.active_locks[user_id]['socket'] == websocket:
                del self.active_locks[user_id]
        
        if websocket in self.socket_locks and user_id in self.socket_locks[websocket]:
            self.socket_locks[websocket].remove(user_id)

    def get_lock_owner(self, user_id: int) -> str | None:
        if user_id in self.active_locks:
            return self.active_locks[user_id]['name']
        return None

manager = ConnectionManager()
