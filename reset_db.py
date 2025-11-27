"""
Script para resetear completamente la base de datos
Elimina todas las tablas y las vuelve a crear
"""
from app.database import engine, Base
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.articulo import Articulo
from app.models.pedido import Pedido
from app.models.detalle_pedido import DetallePedido
from app.models.sesion_log import SesionLog
from app.models.detalle_sesion import DetalleSesion

def reset_database():
    """Elimina todas las tablas y las vuelve a crear"""
    print("🗑️  Eliminando todas las tablas...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tablas eliminadas")
    
    print("\n🔨 Creando tablas nuevamente...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas")
    
    print("\n✨ Base de datos reseteada exitosamente!")

if __name__ == "__main__":
    print("=" * 50)
    print("RESET DE BASE DE DATOS")
    print("=" * 50)
    print("\n⚠️  ADVERTENCIA: Esto eliminará TODOS los datos!")
    
    confirm = input("\n¿Estás seguro? (escribe 'SI' para confirmar): ")
    
    if confirm.upper() == "SI":
        reset_database()
    else:
        print("\n❌ Operación cancelada")
