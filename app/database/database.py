import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "database")
DB_PATH = os.path.join(DB_DIR, "drama.db")

os.makedirs(DB_DIR, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def init_db():
    from . import models  # noqa: F401 — 确保模型被导入
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()
