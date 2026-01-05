# backend/inicializar_db.py
import sys
import os
from dotenv import load_dotenv # <--- Nuevo

# Truco de ruta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal
from models import Base, Usuario, Inventario
from passlib.context import CryptContext

load_dotenv() # <--- Cargamos secretos

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    print("⏳ Conectando a PostgreSQL...")
    
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        
        # Leemos el usuario por defecto desde el .env
        default_user = os.getenv("DEFAULT_ADMIN_USER")
        default_pass = os.getenv("DEFAULT_ADMIN_PASSWORD")

        usuario_existente = db.query(Usuario).filter(Usuario.username == default_user).first()
        
        if not usuario_existente:
            print(f"👤 Creando usuario '{default_user}'...")
            password_segura = pwd_context.hash(default_pass) 
            
            nuevo_admin = Usuario(username=default_user, hashed_password=password_segura, es_admin=True)
            db.add(nuevo_admin)
            
            # Datos de prueba (Inventario)
            if db.query(Inventario).count() == 0:
                db.add(Inventario(codigo_producto="ROS-001", nombre="Rosas Freedom 40cm", cantidad_tallos=5000, precio_unitario=0.25))
                db.add(Inventario(codigo_producto="ROS-002", nombre="Rosas Explorer 50cm", cantidad_tallos=3000, precio_unitario=0.30))
            
            db.commit()
            print(f"✅ ¡Listo! Usuario: {default_user} / Clave: {default_pass}")
        else:
            print(f"👌 El usuario '{default_user}' ya existe.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'db' in locals(): db.close()

if __name__ == "__main__":
    init_db()