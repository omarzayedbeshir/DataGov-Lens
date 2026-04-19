from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from auth import hash_password, get_current_user
import schemas

router = APIRouter()


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        text("SELECT EmailAddress FROM User WHERE EmailAddress = :email"),
        {"email": payload.EmailAddress}
    ).fetchone()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered.")

    db.execute(
        text("""INSERT INTO User (EmailAddress, Username, Password, Country, Gender, Birthdate)
                VALUES (:email, :username, :password, :country, :gender, :birthdate)"""),
        {"email": payload.EmailAddress, "username": payload.Username,
         "password": hash_password(payload.Password), "country": payload.Country,
         "gender": payload.Gender, "birthdate": payload.Birthdate}
    )
    db.commit()

    row = db.execute(
        text("SELECT * FROM User WHERE EmailAddress = :email"),
        {"email": payload.EmailAddress}
    ).mappings().fetchone()
    return dict(row)


@router.get("/me/profile", response_model=schemas.UserResponse)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    return current_user


@router.get("/me/usage", response_model=list[schemas.UsageResponse])
def view_my_usage(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT * FROM ProjectDatasets WHERE UserEmailAddress = :email"),
        {"email": current_user["EmailAddress"]}
    ).mappings().fetchall()
    return [dict(r) for r in rows]


@router.get("/me/projects", response_model=list[schemas.ProjectResponse])
def list_my_projects(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT * FROM Project WHERE UserEmailAddress = :email"),
        {"email": current_user["EmailAddress"]}
    ).mappings().fetchall()
    return [dict(r) for r in rows]
