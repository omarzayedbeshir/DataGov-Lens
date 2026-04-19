from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

ca_cert_path = os.getenv("CA_CERT_PATH", None)

ssl_args = {"ssl": {"ca": ca_cert_path}} if ca_cert_path else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=ssl_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
