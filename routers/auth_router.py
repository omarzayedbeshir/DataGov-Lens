from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from auth import verify_password, create_access_token, blacklist_token, get_current_user, oauth2_scheme
import models

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str
    email: str
    username: str


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login with **email** (in the `username` field) and **password**.
    Returns a Bearer token to use in subsequent requests.
    """
    user = db.get(models.User, form_data.username)
    if not user or not verify_password(form_data.password, user.Password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(email=user.EmailAddress)
    return Token(
        access_token=token,
        token_type="bearer",
        email=user.EmailAddress,
        username=user.Username,
    )


# ── Logout ────────────────────────────────────────────────────────────────────

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    token: str = Depends(oauth2_scheme),
    current_user: models.User = Depends(get_current_user),
):
    """
    Invalidates the current Bearer token.
    The client should also discard the token locally.
    """
    blacklist_token(token)
    return {"message": f"User '{current_user.Username}' logged out successfully."}


# ── Whoami ────────────────────────────────────────────────────────────────────

@router.get("/me")
def whoami(current_user: models.User = Depends(get_current_user)):
    """Returns the currently authenticated user's profile."""
    return {
        "email": current_user.EmailAddress,
        "username": current_user.Username,
        "country": current_user.Country,
        "gender": current_user.Gender,
        "birthdate": str(current_user.Birthdate),
    }
