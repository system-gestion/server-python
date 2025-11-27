from app.database import engine, Base
# Importar modelos para que Base.metadata los reconozca
from app.models import cliente, articulo, pedido, detalle_pedido, monitoreo, usuario, sesion_log, detalle_sesion

print("🗑️  Eliminando todas las tablas...")
from sqlalchemy import text
try:
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS oferta_cliente CASCADE"))
        connection.commit()
except Exception as e:
    print(f"⚠️ No se pudo eliminar tabla oferta_cliente: {e}")

Base.metadata.drop_all(bind=engine)
print("✅ Tablas eliminadas.")

print("✨ Creando tablas nuevamente...")
Base.metadata.create_all(bind=engine)
print("✅ Tablas creadas.")
