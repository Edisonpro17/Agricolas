# backend/fix_inventario.py
import sys
import os

# Truco de ruta para encontrar database.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Inventario

def poblar_inventario():
    print("⏳ Revisando el inventario...")
    db = SessionLocal()
    
    try:
        # Contamos cuántos productos hay
        cantidad = db.query(Inventario).count()
        print(f"🧐 Productos actuales en base de datos: {cantidad}")

        if cantidad == 0:
            print("📭 ¡Está vacío! Insertando productos de prueba...")
            
            # Creamos productos de ejemplo
            prod1 = Inventario(codigo_producto="ROS-001", nombre="Rosas Freedom 40cm", cantidad_tallos=5000, precio_unitario=0.25)
            prod2 = Inventario(codigo_producto="ROS-002", nombre="Rosas Explorer 50cm", cantidad_tallos=3000, precio_unitario=0.30)
            
            db.add(prod1)
            db.add(prod2)
            db.commit()
            print("✅ ¡Productos insertados con éxito!")
        else:
            print("👍 El inventario ya tiene datos. Todo en orden.")

    except Exception as e:
        print(f"❌ Error insertando datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    poblar_inventario()
    