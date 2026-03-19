from sqlalchemy import Column, Integer, String, Float, DateTime, func
from database import Base
from datetime import datetime

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    precio = Column(Float)
    stock = Column(Integer)
    
class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    nombre_producto = Column(String)  # Guardamos el nombre por si el producto se borra después
    cantidad = Column(Integer)
    precio_unitario = Column(Float)
    total_venta = Column(Float)
    fecha = Column(DateTime, default=datetime.now) # Se pone la hora automáticamente

# Nuevo modelo para guardar los cierres de cada día
class CierreDiario(Base):
    __tablename__ = "cierres_diarios"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=func.now())
    total_dia = Column(Float)
    resumen_productos = Column(String) # Aquí guardaremos