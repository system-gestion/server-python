"""
Seeders para poblar la base de datos con datos de prueba.
Ejecutar con: python -m app.seeders.seed

ESTADOS DE PEDIDO:
- 1 = Pendiente (pending)
- 2 = Completado (completed)
- 3 = Cancelado (cancelled)

ESTADOS DE DETALLE PEDIDO:
- 0 = Quitado/Inactivo
- 1 = Activo
"""

from datetime import date
from sqlalchemy.orm import Session
import bcrypt

from app.database import SessionLocal, engine, Base
from app.models.cliente import Cliente
from app.models.articulo import Articulo
from app.models.usuario import Usuario
from app.models.pedido import Pedido
from app.models.detalle_pedido import DetallePedido
from app.models.monitoreo import Monitoreo
from app.models.sesion_log import SesionLog
from app.models.detalle_sesion import DetalleSesion



def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def clear_database(db: Session):
    """Limpia todas las tablas de la base de datos"""
    print("🗑️  Limpiando base de datos...")
    
    # Eliminar en orden inverso de dependencias
    db.query(DetalleSesion).delete()
    db.query(SesionLog).delete()
    db.query(DetallePedido).delete()
    db.query(Pedido).delete()
    db.query(Articulo).delete()
    db.query(Cliente).delete()
    db.query(Usuario).delete()
    db.query(Monitoreo).delete()
    
    db.commit()
    print("✅ Base de datos limpiada")


def seed_clientes(db: Session):
    """Inserta clientes de prueba"""
    print("👥 Insertando clientes...")
    
    clientes = [
        Cliente(
            cod_cliente="CLI001",
            nombre="Juan Pérez García",
            direccion="Av. Principal 123, Lima",
            telefono="555-1234"
        ),
        Cliente(
            cod_cliente="CLI002",
            nombre="María López Rodríguez",
            direccion="Calle Los Olivos 456, Arequipa",
            telefono="555-5678"
        ),
        Cliente(
            cod_cliente="CLI003",
            nombre="Carlos Mendoza Silva",
            direccion="Jr. Las Flores 789, Cusco",
            telefono="555-9012"
        ),
        Cliente(
            cod_cliente="CLI004",
            nombre="Ana Torres Vega",
            direccion="Av. Los Pinos 321, Trujillo",
            telefono="555-3456"
        ),
        Cliente(
            cod_cliente="CLI005",
            nombre="Roberto Sánchez Cruz",
            direccion="Calle San Martín 654, Piura",
            telefono="555-7890"
        ),
    ]
    
    db.add_all(clientes)
    db.commit()
    print(f"✅ {len(clientes)} clientes insertados")


def seed_articulos(db: Session):
    """Inserta artículos de prueba"""
    print("📦 Insertando artículos...")
    
    articulos = [
        Articulo(cod_articulo=101, nombre="Laptop HP 15", pvp=2500.00, stock=15),
        Articulo(cod_articulo=102, nombre="Mouse Logitech", pvp=45.50, stock=50),
        Articulo(cod_articulo=103, nombre="Teclado Mecánico", pvp=120.00, stock=30),
        Articulo(cod_articulo=104, nombre="Monitor LG 24 pulgadas", pvp=680.00, stock=20),
        Articulo(cod_articulo=105, nombre="Impresora Canon", pvp=350.00, stock=12),
        Articulo(cod_articulo=106, nombre="Disco Duro 1TB", pvp=180.00, stock=40),
        Articulo(cod_articulo=107, nombre="Memoria RAM 16GB", pvp=280.00, stock=35),
        Articulo(cod_articulo=108, nombre="Webcam HD", pvp=95.00, stock=25),
        Articulo(cod_articulo=109, nombre="Auriculares Bluetooth", pvp=75.00, stock=60),
        Articulo(cod_articulo=110, nombre="Router WiFi", pvp=150.00, stock=18),
    ]
    
    db.add_all(articulos)
    db.commit()
    print(f"✅ {len(articulos)} artículos insertados")


def seed_usuarios(db: Session):
    """Inserta usuarios de prueba"""
    print("👤 Insertando usuarios...")
    
    usuarios = [
        Usuario(
            cod_usuario=1,
            apellidos="Flores Santos",
            nombres="Erick Stip",
            nivel=1,  # Supervisor
            correo="erick@gmail.com",
            celular="999-111-222",
            fecha_ingreso=date(2024, 1, 15),
            estado=1,
            password=hash_password("123456")
        ),
        Usuario(
            cod_usuario=2,
            apellidos="Caycho",
            nombres="Adriano",
            nivel=2,  # Vendedor
            correo="adriano@gmail.com",
            celular="999-333-444",
            fecha_ingreso=date(2024, 3, 20),
            estado=1,
            password=hash_password("123456")
        ),
        Usuario(
            cod_usuario=3,
            apellidos="Martínez Silva",
            nombres="Ana Lucía",
            nivel=2,  # Vendedor
            correo="ana@gmail.com",
            celular="999-555-666",
            fecha_ingreso=date(2024, 5, 10),
            estado=1,
            password=hash_password("123456")
        ),
        Usuario(
            cod_usuario=4,
            apellidos="Rosales",
            nombres="Luis",
            nivel=3,  # Cliente
            correo="luis@gmail.com",
            celular="999-777-888",
            fecha_ingreso=date(2024, 7, 5),
            estado=1,
            password=hash_password("123456")
        ),
        Usuario(
            cod_usuario=5,
            apellidos="Sánchez Cruz",
            nombres="Laura Patricia",
            nivel=1,  # Supervisor
            correo="laura@gmail.com",
            celular="999-999-000",
            fecha_ingreso=date(2023, 11, 1),
            estado=1,
            password=hash_password("123456")
        ),
    ]
    
    db.add_all(usuarios)
    db.commit()
    print(f"✅ {len(usuarios)} usuarios insertados")
    print("\n📝 Credenciales de prueba:")
    print("   Supervisor: maria.garcia@example.com / supervisor123")
    print("   Vendedor: carlos.rodriguez@example.com / vendedor123")
    print("   Cliente: roberto.torres@example.com / cliente123")


def seed_pedidos(db: Session):
    """Inserta pedidos con detalles de prueba"""
    print("🛒 Insertando pedidos...")
    
    # Pedido 1 - Pendiente
    pedido1 = Pedido(
        num_pedido=1001,
        fecha=date(2025, 11, 1),
        importe=3050.50,
        cod_cliente="CLI001",
        estado=1  # 1 = pending
    )
    db.add(pedido1)
    db.flush()
    
    detalles1 = [
        DetallePedido(num_pedido=1001, cod_articulo=101, cantidad=1, subtotal=2500.00, estado=1),
        DetallePedido(num_pedido=1001, cod_articulo=102, cantidad=5, subtotal=227.50, estado=1),
        DetallePedido(num_pedido=1001, cod_articulo=103, cantidad=2, subtotal=240.00, estado=1),
        DetallePedido(num_pedido=1001, cod_articulo=109, cantidad=1, subtotal=75.00, estado=1),
    ]
    db.add_all(detalles1)
    
    # Pedido 2 - Completado
    pedido2 = Pedido(
        num_pedido=1002,
        fecha=date(2025, 11, 5),
        importe=1040.00,
        cod_cliente="CLI002",
        estado=2  # 2 = completed
    )
    db.add(pedido2)
    db.flush()
    
    detalles2 = [
        DetallePedido(num_pedido=1002, cod_articulo=104, cantidad=1, subtotal=680.00, estado=1),
        DetallePedido(num_pedido=1002, cod_articulo=106, cantidad=2, subtotal=360.00, estado=1),
    ]
    db.add_all(detalles2)
    
    # Pedido 3 - Cancelado
    pedido3 = Pedido(
        num_pedido=1003,
        fecha=date(2025, 11, 8),
        importe=1110.00,
        cod_cliente="CLI003",
        estado=3  # 3 = cancelled
    )
    db.add(pedido3)
    db.flush()
    
    detalles3 = [
        DetallePedido(num_pedido=1003, cod_articulo=105, cantidad=1, subtotal=350.00, estado=1),
        DetallePedido(num_pedido=1003, cod_articulo=107, cantidad=2, subtotal=560.00, estado=1),
        DetallePedido(num_pedido=1003, cod_articulo=110, cantidad=1, subtotal=150.00, estado=1),
        DetallePedido(num_pedido=1003, cod_articulo=108, cantidad=1, subtotal=95.00, estado=0),  # Quitado
    ]
    db.add_all(detalles3)
    
    # Pedido 4 - Pendiente
    pedido4 = Pedido(
        num_pedido=1004,
        fecha=date(2025, 11, 10),
        importe=455.50,
        cod_cliente="CLI004",
        estado=1  # 1 = pending
    )
    db.add(pedido4)
    db.flush()
    
    detalles4 = [
        DetallePedido(num_pedido=1004, cod_articulo=102, cantidad=3, subtotal=136.50, estado=1),
        DetallePedido(num_pedido=1004, cod_articulo=103, cantidad=1, subtotal=120.00, estado=1),
        DetallePedido(num_pedido=1004, cod_articulo=109, cantidad=2, subtotal=150.00, estado=1),
    ]
    db.add_all(detalles4)
    
    db.commit()
    print("✅ 4 pedidos insertados con sus detalles")


def set_sequence_value(db: Session):
    """Actualiza la secuencia de la base de datos al valor máximo actual"""
    # Solo para PostgreSQL
    if 'postgresql' in str(engine.url):
        from sqlalchemy import text
        print("🔄 Actualizando secuencia de pedidos...")
        try:
            db.execute(text("SELECT setval('pedido_num_pedido_seq', (SELECT MAX(num_pedido) FROM pedido));"))
            db.commit()
            print("✅ Secuencia actualizada correctamente")
        except Exception as e:
            print(f"⚠️ No se pudo actualizar la secuencia: {e}")


def run_seeders(clear_first: bool = True):
    """Ejecuta todos los seeders"""
    print("=" * 60)
    print("🌱 INICIANDO SEEDERS")
    print("=" * 60)
    
    # Crear todas las tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        if clear_first:
            clear_database(db)
        
        # Ejecutar seeders en orden
        seed_clientes(db)
        seed_articulos(db)
        seed_usuarios(db)
        seed_pedidos(db)
        
        # Actualizar secuencias
        set_sequence_value(db)
        
        print("\n" + "=" * 60)
        print("✅ SEEDERS COMPLETADOS EXITOSAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error al ejecutar seeders: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seeders()
