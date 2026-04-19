from fastapi import APIRouter, Depends, HTTPException, status
from pymysql.connections import Connection

from database import get_db
from auth import hash_password, get_current_user
import schemas

router = APIRouter()


# ── Register ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: schemas.UserCreate, conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("SELECT EmailAddress FROM User WHERE EmailAddress = %s", (payload.EmailAddress,))
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="Email already registered.")

        cur.execute(
            """INSERT INTO User (EmailAddress, Username, Password, Country, Gender, Birthdate)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (payload.EmailAddress, payload.Username, hash_password(payload.Password),
             payload.Country, payload.Gender, payload.Birthdate)
        )
        conn.commit()

        cur.execute("SELECT * FROM User WHERE EmailAddress = %s", (payload.EmailAddress,))
        return cur.fetchone()


# ── My profile ────────────────────────────────────────────────────────────────

@router.get("/me/profile", response_model=schemas.UserResponse)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    return current_user


# ── My usage ──────────────────────────────────────────────────────────────────

@router.get("/me/usage", response_model=list[schemas.UsageResponse])
def view_my_usage(current_user: dict = Depends(get_current_user), conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM ProjectDatasets WHERE UserEmailAddress = %s",
            (current_user["EmailAddress"],)
        )
        return cur.fetchall()


# ── My projects ───────────────────────────────────────────────────────────────

@router.get("/me/projects", response_model=list[schemas.ProjectResponse])
def list_my_projects(current_user: dict = Depends(get_current_user), conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM Project WHERE UserEmailAddress = %s",
            (current_user["EmailAddress"],)
        )
        return cur.fetchall()
