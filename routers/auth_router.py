from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymysql.connections import Connection
from pydantic import BaseModel

from database import get_db
from auth import verify_password, create_access_token, blacklist_token, get_current_user, oauth2_scheme

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str
    email: str
    username: str


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), conn: Connection = Depends(get_db)):
    """Login with email (username field) and password. Returns a Bearer token."""
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM User WHERE EmailAddress = %s", (form_data.username,))
        user = cur.fetchone()

    if not user or not verify_password(form_data.password, user["Password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(email=user["EmailAddress"])
    return Token(
        access_token=token,
        token_type="bearer",
        email=user["EmailAddress"],
        username=user["Username"],
    )


# ── Logout ────────────────────────────────────────────────────────────────────

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(token: str = Depends(oauth2_scheme), current_user: dict = Depends(get_current_user)):
    """Invalidates the current Bearer token."""
    blacklist_token(token)
    return {"message": f"User '{current_user['Username']}' logged out successfully."}


# ── Whoami ────────────────────────────────────────────────────────────────────

@router.get("/me")
def whoami(current_user: dict = Depends(get_current_user)):
    return {
        "email":     current_user["EmailAddress"],
        "username":  current_user["Username"],
        "country":   current_user["Country"],
        "gender":    current_user["Gender"],
        "birthdate": str(current_user["Birthdate"]),
    }
