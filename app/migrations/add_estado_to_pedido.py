"""
Script de migración para agregar columna 'estado' a la tabla 'pedido'
Ejecutar con: python -m app.migrations.add_estado_to_pedido
"""
from sqlalchemy import text
from app.database import engine, SessionLocal

def migrate():
    """Agregar columna estado a tabla pedido"""
    db = SessionLocal()
    
    try:
        print("Iniciando migración: Agregar columna 'estado' a tabla 'pedido'...")
        
        # Verificar si la columna ya existe
        check_column = text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('pedido') 
            WHERE name='estado'
        """)
        
        result = db.execute(check_column).scalar()
        
        if result > 0:
            print("⚠️  La columna 'estado' ya existe en la tabla 'pedido'. Migración omitida.")
            return
        
        # Agregar columna estado con valor por defecto 'pending'
        alter_table = text("""
            ALTER TABLE pedido 
            ADD COLUMN estado VARCHAR(20) NOT NULL DEFAULT 'pending'
        """)
        
        db.execute(alter_table)
        db.commit()
        
        print("✅ Migración completada exitosamente!")
        print("   - Columna 'estado' agregada a tabla 'pedido'")
        print("   - Valor por defecto: 'pending'")
        print("   - Valores permitidos: 'pending', 'completed', 'cancelled'")
        
        # Verificar registros actualizados
        count_query = text("SELECT COUNT(*) FROM pedido WHERE estado = 'pending'")
        count = db.execute(count_query).scalar()
        print(f"   - {count} pedidos existentes marcados como 'pending'")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error durante la migración: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
