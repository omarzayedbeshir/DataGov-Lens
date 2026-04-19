import pymysql
import pymysql.cursors
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "database": os.getenv("DB_NAME", "DataGovApp"),
    "cursorclass": pymysql.cursors.DictCursor,
    "charset": "utf8mb4",
}


def get_connection():
    return pymysql.connect(**DB_CONFIG)


def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
