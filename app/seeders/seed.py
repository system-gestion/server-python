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
    print("Limpiando base de datos...")
    
    # Eliminar en orden inverso de dependencias
    from sqlalchemy import text
    try:
        db.execute(text("DROP TABLE IF EXISTS oferta_cliente CASCADE"))
        db.commit()
    except Exception as e:
        print(f"⚠️ No se pudo eliminar tabla oferta_cliente: {e}")
        db.rollback()

    db.query(DetalleSesion).delete()
    db.query(SesionLog).delete()
    db.query(DetallePedido).delete()
    db.query(Pedido).delete()
    db.query(Articulo).delete()
    db.query(Cliente).delete()
    db.query(Usuario).delete()
    db.query(Monitoreo).delete()
    
    db.commit()
    print("Base de datos limpiada")


def seed_articulos(db: Session):
    """Inserta artículos de prueba"""
    print("📦 Insertando artículos...")
    
    articulos = [
        Articulo(cod_articulo=101, nombre="Laptop HP 15", pvp=2500.00, stock=15, tipo_descuento=1, valor_descuento=200.00), # Descuento fijo
        Articulo(cod_articulo=102, nombre="Mouse Logitech", pvp=45.50, stock=50, tipo_descuento=2, valor_descuento=10.0), # Descuento 10%
        Articulo(cod_articulo=103, nombre="Teclado Mecánico", pvp=120.00, stock=30),
        Articulo(cod_articulo=104, nombre="Monitor LG 24 pulgadas", pvp=680.00, stock=20),
        Articulo(cod_articulo=105, nombre="Impresora Canon", pvp=350.00, stock=12),
        Articulo(cod_articulo=106, nombre="Disco Duro 1TB", pvp=180.00, stock=40),
        Articulo(cod_articulo=107, nombre="Memoria RAM 16GB", pvp=280.00, stock=35),
        Articulo(cod_articulo=108, nombre="Webcam HD", pvp=95.00, stock=25),
        Articulo(cod_articulo=109, nombre="Auriculares Bluetooth", pvp=75.00, stock=60, tipo_descuento=2, valor_descuento=15.0), # Descuento 15%
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
            apellidos="Pérez García",
            nombres="Juan",
            nivel=3,  # Cliente
            correo="juan@gmail.com",
            celular="555-1234",
            fecha_ingreso=date(2024, 7, 5),
            estado=1,
            password=hash_password("123456")
        ),
        Usuario(
            cod_usuario=5,
            apellidos="López Rodríguez",
            nombres="María",
            nivel=3,  # Cliente
            correo="maria@gmail.com",
            celular="555-5678",
            fecha_ingreso=date(2024, 8, 10),
            estado=1,
            password=hash_password("123456")
        ),
        Usuario(
            cod_usuario=6,
            apellidos="Mendoza Silva",
            nombres="Carlos",
            nivel=3,  # Cliente
            correo="carlos@gmail.com",
            celular="555-9012",
            fecha_ingreso=date(2024, 9, 1),
            estado=1,
            password=hash_password("123456")
        ),
        Usuario(
            cod_usuario=7,
            apellidos="Torres Vega",
            nombres="Ana",
            nivel=3,  # Cliente
            correo="ana.torres@gmail.com",
            celular="555-3456",
            fecha_ingreso=date(2024, 10, 5),
            estado=1,
            password=hash_password("123456")
        ),
        Usuario(
            cod_usuario=8,
            apellidos="Sánchez Cruz",
            nombres="Roberto",
            nivel=3,  # Cliente
            correo="roberto@gmail.com",
            celular="555-7890",
            fecha_ingreso=date(2024, 11, 1),
            estado=1,
            password=hash_password("123456")
        ),
    ]
    
    db.add_all(usuarios)
    db.commit()
    print(f"✅ {len(usuarios)} usuarios insertados")
    print("\n📝 Credenciales de prueba:")
    print("   Supervisor: erick@gmail.com / 123456")
    print("   Vendedor: adriano@gmail.com / 123456")
    print("   Cliente: juan@gmail.com / 123456")

def seed_clientes(db: Session):
    """Inserta clientes de prueba (sincronizados con usuarios nivel 3)"""
    print("👥 Insertando clientes...")
    
    clientes = [
        Cliente(
            cod_cliente="CLI001",
            nombre="Juan Pérez García",
            direccion="Av. Principal 123, Lima",
            telefono="555-1234",
            cod_usuario=4  # Juan (Cliente)
        ),
        Cliente(
            cod_cliente="CLI002",
            nombre="María López Rodríguez",
            direccion="Calle Los Olivos 456, Arequipa",
            telefono="555-5678",
            cod_usuario=5  # María (Cliente)
        ),
        Cliente(
            cod_cliente="CLI003",
            nombre="Carlos Mendoza Silva",
            direccion="Jr. Las Flores 789, Cusco",
            telefono="555-9012",
            cod_usuario=6  # Carlos (Cliente)
        ),
        Cliente(
            cod_cliente="CLI004",
            nombre="Ana Torres Vega",
            direccion="Av. Los Pinos 321, Trujillo",
            telefono="555-3456",
            cod_usuario=7  # Ana (Cliente)
        ),
        Cliente(
            cod_cliente="CLI005",
            nombre="Roberto Sánchez Cruz",
            direccion="Calle San Martín 654, Piura",
            telefono="555-7890",
            cod_usuario=8  # Roberto (Cliente)
        ),
    ]
    
    db.add_all(clientes)
    db.commit()
    print(f"✅ {len(clientes)} clientes insertados")

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
        print("🔄 Actualizando secuencias...")
        try:
            db.execute(text("SELECT setval('pedido_num_pedido_seq', (SELECT MAX(num_pedido) FROM pedido));"))
            db.execute(text("SELECT setval('usuario_cod_usuario_seq', (SELECT MAX(cod_usuario) FROM usuario));"))
            db.commit()
            print("✅ Secuencias actualizadas correctamente")
        except Exception as e:
            print(f"⚠️ No se pudo actualizar las secuencias: {e}")


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
        seed_usuarios(db)
        seed_clientes(db)
        seed_articulos(db)
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
