# backend/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from database import Base
import datetime

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String) 
    es_admin = Column(Boolean, default=False)

class Inventario(Base):
    __tablename__ = "inventario"

    id = Column(Integer, primary_key=True, index=True)
    codigo_producto = Column(String, unique=True, index=True)
    nombre = Column(String)
    cantidad_tallos = Column(Integer, default=0)
    precio_unitario = Column(Float, default=0.0)
    ultima_actualizacion = Column(DateTime, default=datetime.datetime.utcnow)