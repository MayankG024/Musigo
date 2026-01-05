"""Authentication endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional

from api.core.database import get_db
from api.core.security import hash_password, verify_password, create_access_token
from models.user import User

router = APIRouter(tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


class AuthUser(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser


async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    """Return a shared demo user without requiring authentication.

    If the demo user doesn't exist yet, create it on the fly. This makes all
    user-scoped features (favorites, playlists, activity) publicly accessible
    under a single shared identity.
    """
    result = await db.execute(select(User).where(User.username == "demo"))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            email="demo@musigo.local",
            username="demo",
            hashed_password=hash_password("demo"),
            full_name="Demo User",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user and return auth token"""
    # Check if user exists
    result = await db.execute(
        select(User).where((User.email == user_data.email) | (User.username == user_data.username))
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.username, "uid": user.id})
    return AuthResponse(access_token=access_token, user=user)


@router.post("/login", response_model=AuthResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Login using username (form field 'username') and return token + user"""
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username, "uid": user.id})
    return AuthResponse(access_token=access_token, user=user)


class LoginJSON(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str


@router.post("/login/json", response_model=AuthResponse)
async def login_json(payload: LoginJSON, db: AsyncSession = Depends(get_db)):
    """JSON login supporting either email or username."""
    if not payload.username and not payload.email:
        raise HTTPException(status_code=400, detail="Username or email required")
    stmt = select(User).where(User.username == payload.username) if payload.username else select(User).where(User.email == payload.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    access_token = create_access_token(data={"sub": user.username, "uid": user.id})
    return AuthResponse(access_token=access_token, user=user)


@router.get("/me", response_model=AuthUser)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


@router.patch("/profile", response_model=AuthUser)
async def update_profile(update: ProfileUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    changed = False
    for field in ["full_name", "bio", "avatar_url"]:
        value = getattr(update, field)
        if value is not None:
            setattr(current_user, field, value)
            changed = True
    if changed:
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
    return current_user


@router.post("/logout")
async def logout():
    """Stateless logout (client should discard token)."""
    return {"detail": "Logged out"}
