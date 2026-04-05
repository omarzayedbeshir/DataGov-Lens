from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os
import ssl
import base64
import tempfile

ca_cert_b64 = os.environ["DB_CA_CERT"]
ca_cert_pem = base64.b64decode(ca_cert_b64)

with tempfile.NamedTemporaryFile(delete=False, suffix=".pem") as f:
    f.write(ca_cert_pem)
    ca_cert_path = f.name

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=False, connect_args={"ssl": {"ca": ca_cert_path}})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
