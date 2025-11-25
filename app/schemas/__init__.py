# Schemas de validación con Pydantic

from app.schemas.auth import UsuarioLogin, LoginResponse, LogoutResponse, MeResponse
from app.schemas.usuario import (
    UsuarioBase,
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioOnline
)
from app.schemas.cliente import ClienteBase, ClienteCreate, ClienteUpdate, ClienteResponse
from app.schemas.articulo import ArticuloBase, ArticuloCreate, ArticuloUpdate, ArticuloResponse
from app.schemas.pedido import (
    DetallePedidoBase,
    DetallePedidoCreate,
    DetallePedidoResponse,
    PedidoBase,
    PedidoCreate,
    PedidoUpdate,
    PedidoResponse
)
from app.schemas.comision import ComisionResponse, ComisionDetalle
from app.schemas.auditoria import SesionLogResponse, DetalleSesionResponse

__all__ = [
    # Auth
    "UsuarioLogin",
    "LoginResponse",
    "LogoutResponse",
    "MeResponse",
    # Usuario
    "UsuarioBase",
    "UsuarioCreate",
    "UsuarioUpdate",
    "UsuarioResponse",
    "UsuarioOnline",
    # Cliente
    "ClienteBase",
    "ClienteCreate",
    "ClienteUpdate",
    "ClienteResponse",
    # Articulo
    "ArticuloBase",
    "ArticuloCreate",
    "ArticuloUpdate",
    "ArticuloResponse",
    # Pedido
    "DetallePedidoBase",
    "DetallePedidoCreate",
    "DetallePedidoResponse",
    "PedidoBase",
    "PedidoCreate",
    "PedidoUpdate",
    "PedidoResponse",
    # Comision
    "ComisionResponse",
    # Auditoria
    "SesionLogResponse",
    "DetalleSesionResponse",
]
