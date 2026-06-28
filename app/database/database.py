from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

# Load variables from .env to allow python to read.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)#bridge to PostgreSQL

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)#communicates with the db.

Base = declarative_base()#close


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()