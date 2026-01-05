"""Music endpoints"""

from fastapi import APIRouter, Depends, Query, Request
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, desc

from api.core.database import get_db
from api.core.rate_limit import limiter
from models.music import Song

router = APIRouter()


class SongResponse(BaseModel):
    id: int
    title: str
    artist: str
    album: Optional[str]
    duration_ms: Optional[int]
    preview_url: Optional[str]
    album_art_url: Optional[str]


@router.get("/search", response_model=List[SongResponse])
@limiter.limit("100/minute")
async def search_songs(
    request: Request,
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Search for songs by title, artist, or album"""
    search_term = f"%{q}%"
    stmt = (
        select(Song)
        .where(
            or_(
                Song.title.ilike(search_term),
                Song.artist.ilike(search_term),
                Song.album.ilike(search_term)
            )
        )
        .order_by(desc(Song.play_count))
        .limit(limit)
    )
    result = await db.execute(stmt)
    songs = result.scalars().all()
    
    return [
        SongResponse(
            id=song.id,
            title=song.title,
            artist=song.artist,
            album=song.album,
            duration_ms=song.duration_ms,
            preview_url=song.preview_url,
            album_art_url=song.album_art_url
        )
        for song in songs
    ]


@router.get("/trending", response_model=List[SongResponse])
@limiter.limit("100/minute")
async def get_trending(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get trending songs based on play count and recent activity"""
    stmt = (
        select(Song)
        .order_by(desc(Song.play_count), desc(Song.like_count))
        .limit(limit)
    )
    result = await db.execute(stmt)
    songs = result.scalars().all()
    
    return [
        SongResponse(
            id=song.id,
            title=song.title,
            artist=song.artist,
            album=song.album,
            duration_ms=song.duration_ms,
            preview_url=song.preview_url,
            album_art_url=song.album_art_url
        )
        for song in songs
    ]
