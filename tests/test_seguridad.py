# tests/test_seguridad.py
from fastapi.testclient import TestClient
import sys
import os
from dotenv import load_dotenv # <--- Nuevo

# Cargar variables para saber con qué probar
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.main import app

client = TestClient(app)

# Leemos las credenciales esperadas
TEST_USER = os.getenv("DEFAULT_ADMIN_USER")
TEST_PASS = os.getenv("DEFAULT_ADMIN_PASSWORD")

def test_1_login_exitoso():
    print(f"\n🧪 TEST 1: Login con usuario '{TEST_USER}'...")
    # Usamos las variables, no texto fijo
    response = client.post("/token", data={"username": TEST_USER, "password": TEST_PASS})
    
    assert response.status_code == 200, f"Falló el login: {response.text}"
    token = response.json()["access_token"]
    print("✅ ¡Éxito! Token recibido.")
    return token

def test_2_login_hacker():
    print("\n🧪 TEST 2: Intento de Login 'Hacker'...")
    # Probamos con una clave que sabemos que es incorrecta
    response = client.post("/token", data={"username": TEST_USER, "password": "CLAVE_MALA_999"})
    assert response.status_code == 401
    print("✅ ¡Éxito! Bloqueado.")

def test_3_acceso_inventario():
    print("\n🧪 TEST 3: Acceso a Inventario...")
    # Login primero
    response_login = client.post("/token", data={"username": TEST_USER, "password": TEST_PASS})
    token = response_login.json()["access_token"]
    
    # Acceso a datos
    headers = {"Authorization": f"Bearer {token}"}
    response_inv = client.get("/inventario", headers=headers)
    
    assert response_inv.status_code == 200
    assert len(response_inv.json()) > 0
    print(f"✅ ¡Éxito! Inventario leído.")

if __name__ == "__main__":
    try:
        test_1_login_exitoso()
        test_2_login_hacker()
        test_3_acceso_inventario()
        print("\n🏆 SISTEMA ALINEADO CON .ENV Y SEGURO.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")