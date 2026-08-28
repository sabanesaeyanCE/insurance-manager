from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL
from src.database.base import Base
import src.database.models

# Create Engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Enable Foreign Key constraints explicitly for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def init_db():
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    """ایجاد، مدیریت و بستن خودکار سشن دیتابیس برای جلوگیری از قفل شدن دیتابیس"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()