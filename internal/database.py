from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Stringa di connessione (SQLite crea un file locale chiamato 'test.db')
SQLALCHEMY_DATABASE_URL = "sqlite:///./nps_project.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       "check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass

# Questa funzione serve a FastAPI per aprire/chiudere la connessione a ogni richiesta


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
