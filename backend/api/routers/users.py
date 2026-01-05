"""User endpoints"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.routers.auth import get_current_user
from models.user import User

router = APIRouter()


class UserProfile(BaseModel):
    id: int
    username: str
    full_name: str
    bio: str


@router.get("/me", response_model=UserProfile)
async def get_user_profile(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get current authenticated user profile"""
    return UserProfile(
        id=user.id,
        username=user.username,
        full_name=user.full_name or "",
        bio=user.bio or ""
    )
