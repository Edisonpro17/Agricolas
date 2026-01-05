# backend/admin_gestionar_usuarios.py
import sys
import os
from sqlalchemy.exc import IntegrityError

# Configuración de rutas para encontrar tu base de datos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Usuario
from passlib.context import CryptContext

# Herramienta de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gestionar_credenciales():
    print("\n🔧 --- GESTOR DE USUARIOS Y CONTRASEÑAS --- 🔧")
    
    # 1. Identificar al usuario
    usuario_actual = input("1. Ingresa el usuario ACTUAL que quieres modificar (ej. admin): ")
    
    db = SessionLocal()
    try:
        # Buscamos al usuario
        user_db = db.query(Usuario).filter(Usuario.username == usuario_actual).first()
        
        if not user_db:
            print(f"❌ Error: El usuario '{usuario_actual}' NO existe.")
            return

        print(f"✅ Usuario encontrado: {user_db.username}")
        print("--- Deja en blanco (Enter) lo que NO quieras cambiar ---")
        
        # 2. Pedir nuevos datos
        nuevo_usuario = input(f"2. Nuevo nombre de usuario (Actual: {user_db.username}): ").strip()
        nueva_clave = input("3. Nueva contraseña: ").strip()
        
        cambios_hechos = False

        # --- CAMBIO DE NOMBRE DE USUARIO ---
        if nuevo_usuario and nuevo_usuario != user_db.username:
            # Verificamos que el nombre nuevo no esté ocupado por otra persona
            existe = db.query(Usuario).filter(Usuario.username == nuevo_usuario).first()
            if existe:
                print(f"⚠️  Error: El nombre '{nuevo_usuario}' ya está en uso. No se cambió el nombre.")
            else:
                print(f"🔄 Cambiando nombre: {user_db.username} -> {nuevo_usuario}")
                user_db.username = nuevo_usuario
                cambios_hechos = True

        # --- CAMBIO DE CONTRASEÑA ---
        if nueva_clave:
            print("🔄 Encriptando y actualizando contraseña...")
            user_db.hashed_password = pwd_context.hash(nueva_clave)
            cambios_hechos = True

        # 3. Guardar cambios
        if cambios_hechos:
            db.commit()
            print("\n✨ ¡CAMBIOS GUARDADOS CON ÉXITO! ✨")
            print(f"Usuario final: {user_db.username}")
            if nueva_clave:
                print("Contraseña: [Actualizada]")
        else:
            print("\nBip bup... No ingresaste datos nuevos. Nada cambió.")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")
        db.rollback() # Deshacer cambios si hubo error
    finally:
        db.close()

if __name__ == "__main__":
    gestionar_credenciales()