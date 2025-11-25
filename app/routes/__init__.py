"""
Inicialización del paquete routes
Exporta todos los routers disponibles
"""
from app.routes import auth, usuarios, clientes, pedidos, articulos, auditoria, comisiones

__all__ = ["auth", "usuarios", "clientes", "pedidos", "articulos", "auditoria", "comisiones"]
