from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency FastAPI : ouvre une session DB pour la durée de la requête,
    la ferme systématiquement ensuite (même en cas d'exception).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
