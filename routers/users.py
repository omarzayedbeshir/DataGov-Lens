from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth import hash_password, get_current_user
import models, schemas

router = APIRouter()


# ── Register ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user. No token required."""
    existing = db.get(models.User, payload.EmailAddress)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered.")

    user = models.User(
        EmailAddress=payload.EmailAddress,
        Username=payload.Username,
        Password=hash_password(payload.Password),
        Country=payload.Country,
        Gender=payload.Gender,
        Birthdate=payload.Birthdate,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Get user ──────────────────────────────────────────────────────────────────

@router.get("/me/profile", response_model=schemas.UserResponse)
def get_my_profile(current_user: models.User = Depends(get_current_user)):
    """Get the logged-in user's profile. Requires authentication."""
    return current_user


# ── View usage ────────────────────────────────────────────────────────────────

@router.get("/me/usage", response_model=list[schemas.UsageResponse])
def view_my_usage(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """View all dataset usages for the logged-in user. Requires authentication."""
    return (
        db.query(models.ProjectDatasets)
        .filter(models.ProjectDatasets.UserEmailAddress == current_user.EmailAddress)
        .all()
    )


# ── List user's projects ───────────────────────────────────────────────────────

@router.get("/me/projects", response_model=list[schemas.ProjectResponse])
def list_my_projects(current_user: models.User = Depends(get_current_user)):
    """List all projects for the logged-in user. Requires authentication."""
    return current_user.projects
