from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Mantiene las conexiones activas: {supervisor_id: WebSocket}
        self.active_connections: List[WebSocket] = []
        
        # Mantiene los bloqueos de USUARIOS: {user_id_to_edit: {'socket': WebSocket, 'name': str}}
        self.active_user_locks: Dict[int, dict] = {}
        
        # Mantiene los bloqueos de CLIENTES: {cliente_id_to_edit: {'socket': WebSocket, 'name': str}}
        self.active_client_locks: Dict[str, dict] = {}
        
        # Mapeo inverso para saber qué locks tiene un socket (para limpieza)
        # {websocket: [user_id_locked]}
        self.socket_user_locks: Dict[WebSocket, List[int]] = {}
        
        # Mapeo inverso para saber qué locks de clientes tiene un socket
        # {websocket: [cliente_id_locked]}
        self.socket_client_locks: Dict[WebSocket, List[str]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.socket_user_locks[websocket] = []
        self.socket_client_locks[websocket] = []

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Liberar locks de usuarios asociados a este socket
        if websocket in self.socket_user_locks:
            for user_id in self.socket_user_locks[websocket]:
                if user_id in self.active_user_locks:
                    # Verificar que el lock realmente pertenece a este socket antes de borrar
                    # (aunque socket_user_locks debería estar sincronizado)
                    if self.active_user_locks[user_id]['socket'] == websocket:
                        del self.active_user_locks[user_id]
            del self.socket_user_locks[websocket]
        
        # Liberar locks de clientes asociados a este socket
        if websocket in self.socket_client_locks:
            for cliente_id in self.socket_client_locks[websocket]:
                if cliente_id in self.active_client_locks:
                    if self.active_client_locks[cliente_id]['socket'] == websocket:
                        del self.active_client_locks[cliente_id]
            del self.socket_client_locks[websocket]

    async def request_lock(self, websocket: WebSocket, user_id: int, supervisor_name: str) -> bool:
        """
        Intenta adquirir un lock para editar un usuario.
        Retorna True si se otorga, False si ya está bloqueado por otro socket.
        """
        if user_id in self.active_user_locks:
            current_lock = self.active_user_locks[user_id]
            # Si el lock pertenece al MISMO socket, permitimos (idempotencia)
            if current_lock['socket'] == websocket:
                return True
            # Si es otro socket, denegamos (incluso si es el mismo usuario en otra pestaña)
            return False
        
        # Otorgar lock
        self.active_user_locks[user_id] = {'socket': websocket, 'name': supervisor_name}
        if websocket in self.socket_user_locks:
            self.socket_user_locks[websocket].append(user_id)
        return True

    async def release_lock(self, websocket: WebSocket, user_id: int):
        """
        Libera el lock de un usuario si pertenece al socket solicitante.
        """
        if user_id in self.active_user_locks:
            if self.active_user_locks[user_id]['socket'] == websocket:
                del self.active_user_locks[user_id]
        
        if websocket in self.socket_user_locks and user_id in self.socket_user_locks[websocket]:
            self.socket_user_locks[websocket].remove(user_id)

    def get_lock_owner(self, user_id: int) -> str | None:
        if user_id in self.active_user_locks:
            return self.active_user_locks[user_id]['name']
        return None

    # Métodos para gestionar locks de CLIENTES
    async def request_client_lock(self, websocket: WebSocket, cliente_id: str, vendedor_name: str) -> bool:
        """
        Intenta adquirir un lock para editar un cliente.
        Retorna True si se otorga, False si ya está bloqueado por otro socket.
        """
        if cliente_id in self.active_client_locks:
            current_lock = self.active_client_locks[cliente_id]
            # Si el lock pertenece al MISMO socket, permitimos (idempotencia)
            if current_lock['socket'] == websocket:
                return True
            # Si es otro socket, denegamos
            return False
        
        # Otorgar lock
        self.active_client_locks[cliente_id] = {'socket': websocket, 'name': vendedor_name}
        if websocket in self.socket_client_locks:
            self.socket_client_locks[websocket].append(cliente_id)
        return True

    async def release_client_lock(self, websocket: WebSocket, cliente_id: str):
        """
        Libera el lock de un cliente si pertenece al socket solicitante.
        """
        if cliente_id in self.active_client_locks:
            if self.active_client_locks[cliente_id]['socket'] == websocket:
                del self.active_client_locks[cliente_id]
        
        if websocket in self.socket_client_locks and cliente_id in self.socket_client_locks[websocket]:
            self.socket_client_locks[websocket].remove(cliente_id)

    def get_client_lock_owner(self, cliente_id: str) -> str | None:
        if cliente_id in self.active_client_locks:
            return self.active_client_locks[cliente_id]['name']
        return None

manager = ConnectionManager()
