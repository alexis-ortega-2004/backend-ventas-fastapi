from sqlalchemy import Column, Integer, String, Float, DateTime
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

    