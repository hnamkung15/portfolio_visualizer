import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.makedirs("data", exist_ok=True)

DATABASE_URL = "sqlite:///./data/portfolio.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
