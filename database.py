import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./ventas.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 1. La fábrica de sesiones (El encargado de abrir y cerrar el libro)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. La base para los modelos (El molde maestro para tus tablas)
Base = declarative_base()


