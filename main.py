from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
from pydantic import BaseModel
from sqlalchemy import func 

# Esto busca nuevas tablas y las crea sin tocar las anteriores
models.Base.metadata.create_all(bind=engine)

# Esto asegura que las tablas existan en ventas.db
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de ventas")

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite que cualquier página (index.html) se conecte
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Permite enviar cualquier tipo de cabecera
)

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
    stock: int = 0

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

# Seccion de VENTAS.
@app.post("/vender/{producto_id}")
def realizar_venta(producto_id: int, cantidad: int, db: Session = Depends(get_db)):
    # 1. Busca el producto
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if producto.stock < cantidad:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente. Solo quedan {producto.stock}")
    # menorar producto vendido de stock
    producto.stock = producto.stock - cantidad
    # 2. Calcular el total de esta transacción
    total_operacion = producto.precio * cantidad
    
    # 3. Guardar el registro en la nueva tabla 'ventas'
    nueva_venta = models.Venta(
        nombre_producto=producto.nombre,
        cantidad=cantidad,
        precio_unitario=producto.precio,
        total_venta=total_operacion
    )
    
    db.add(nueva_venta)
    db.commit()
    
    return {
        "status": "success",
        "mensaje": f"Venta de {producto.nombre} registrada",
        "total": total_operacion
    }

@app.get("/ventas/total-general")
def obtener_total_general(db: Session = Depends(get_db)):
    # Sumamos todos los valores de la columna 'total_venta'
    total = db.query(func.sum(models.Venta.total_venta)).scalar() or 0
    return {"total_acumulado": total}

# Endpoint para aumentar el stock (Reabastecimiento)
@app.put("/productos/{producto_id}/reabastecer")
def reabastecer_stock(producto_id: int, cantidad_nueva: int, db: Session = Depends(get_db)):
    # Buscar el producto en la base de datos
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    
    #  Si el producto no existe, lanzamos error 404
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Sumamos la nueva cantidad al stock que ya tenemos
    producto.stock += cantidad_nueva
    
    #  Guardamos los cambios
    db.commit()
    db.refresh(producto)
    
    return {
        "status": "success",
        "mensaje": f"Se han añadido {cantidad_nueva} unidades a {producto.nombre}",
        "stock_actual": producto.stock
    }