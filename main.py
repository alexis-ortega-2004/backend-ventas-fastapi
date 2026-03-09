from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
from pydantic import BaseModel

# Esto asegura que las tablas existan en ventas.db
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de ventas")

# El "túnel" de conexión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido el servidor de ventas esta activo"}

# Ruta que consulta la base de datos
@app.get("/productos")
def obtener_productos(db: Session = Depends(get_db)):
    # Aquí le pedimos a la DB que traiga todo de la tabla 'producto'
    lista_productos = db.query(models.Producto).all()
    return lista_productos

class ProductoCrear(BaseModel):
    nombre: str
    precio: float
    stock: int

    class Config:
        from_attributes = True
# Esta es la ruta para CREAR productos (POST)
@app.post("/productos")
def crear_producto(item: ProductoCrear, db: Session = Depends(get_db)):
    # Creamos el objeto basado en tu modelo de base de datos
    nuevo_producto = models.Producto(
        nombre=item.nombre, 
        precio=item.precio, 
        stock=item.stock
    )
    db.add(nuevo_producto) # Lo preparamos
    db.commit()            # Lo guardamos físicamente
    db.refresh(nuevo_producto) # Recargamos para ver el ID que le puso la DB
    return nuevo_producto
@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    # 1. Buscamos el producto por su ID
    producto_db = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    
    # 2. Si no existe, avisamos
    if not producto_db:
        return {"error": "Producto no encontrado"}
    
    # 3. Si existe, lo borramos de la DB
    db.delete(producto_db)
    db.commit()
    return {"mensaje": f"Producto con ID {producto_id} eliminado correctamente"}

# RUTA PARA ACTUALIZAR
@app.put("/productos/{producto_id}")
def actualizar_producto(producto_id: int, producto_actualizado: ProductoCrear, db: Session = Depends(get_db)):
    db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not db_producto:
        return {"error": "Lo siento, el producto con ese ID no existe en el sistema."}

    db_producto.nombre = producto_actualizado.nombre
    db_producto.precio = producto_actualizado.precio
    db_producto.cantidad = producto_actualizado.cantidad
    db.commit()
    db.refresh(db_producto)
    return {"mensaje": "¡Producto actualizado con éxito!", "producto_nuevo": db_producto}
