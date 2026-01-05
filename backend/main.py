# backend/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, status, Request # <--- Agregamos Request
from fastapi.responses import FileResponse, JSONResponse # <--- Agregamos JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os
import sys
import pandas as pd
import io
import shutil
import tempfile
import datetime

# --- 👋 NUEVO: IMPORTACIONES PARA LIMITAR INTENTOS ---
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Cargar .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "clave_insegura")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import get_db
from models import Usuario, Inventario
from Generador_de_XML_a_Excel import procesar_excel_web

# --- 👋 NUEVO: CONFIGURAR EL PORTERO (LIMITER) ---
# Usamos la IP del usuario para saber quién es
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Facturación API Segura + DB")

# --- 👋 NUEVO: CONECTAR EL PORTERO A LA APP ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_GENERADOS = os.path.join(BASE_DIR, "..", "GENERADOS")
DIR_FIRMADOS = os.path.join(BASE_DIR, "..", "FIRMADOS")
os.makedirs(DIR_GENERADOS, exist_ok=True)
os.makedirs(DIR_FIRMADOS, exist_ok=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ProductoSchema(BaseModel):
    codigo_producto: str
    nombre: str
    cantidad_tallos: int
    precio_unitario: float
    ultima_actualizacion: datetime.datetime
    class Config:
        from_attributes = True

def verificar_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def obtener_usuario(db: Session, username: str):
    return db.query(Usuario).filter(Usuario.username == username).first()

# --- RUTAS ---

# 👋 NUEVO: APLICAMOS EL LÍMITE AQUÍ (Login)
# "5/minute" significa: Máximo 5 intentos por minuto.
@app.post("/token")
@limiter.limit("5/minute") 
async def login(
    request: Request, # <--- Necesario para que slowapi lea la IP
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = obtener_usuario(db, form_data.username)
    if not user or not verificar_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user.username, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = obtener_usuario(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def home():
    return FileResponse(os.path.join(BASE_DIR, "..", "frontend", "index.html"))

@app.get("/inventario", response_model=List[ProductoSchema])
def leer_inventario(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    productos = db.query(Inventario).all()
    return productos

@app.post("/procesar-facturas")
async def procesar_facturas_endpoint(
    file_excel: UploadFile = File(...), 
    file_firma: UploadFile = File(...),
    clave_firma: str = Form(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".p12") as tmp_p12:
            shutil.copyfileobj(file_firma.file, tmp_p12)
            ruta_temporal_p12 = tmp_p12.name

        contents = await file_excel.read()
        xls = pd.ExcelFile(io.BytesIO(contents))
        target_sheet = "REPORTE FACTURACION"
        df = pd.read_excel(xls, sheet_name=target_sheet if target_sheet in xls.sheet_names else xls.sheet_names[0])

        resultados = procesar_excel_web(df, DIR_GENERADOS, DIR_FIRMADOS, ruta_temporal_p12, clave_firma)

        return {
            "estado": "Proceso finalizado",
            "usuario": current_user.username,
            "total_procesados": len(resultados),
            "detalle": resultados
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
    finally:
        if 'ruta_temporal_p12' in locals() and os.path.exists(ruta_temporal_p12):
            os.remove(ruta_temporal_p12)