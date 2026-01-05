"""Song catalog endpoints (search, trending, detail)"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from pydantic import BaseModel
from typing import List, Optional

from api.core.database import get_db
from models.music import Song
from services import spotify_service

router = APIRouter(tags=["songs"])  # prefix applied in main include


class SongOut(BaseModel):
    song_id: int
    title: str
    artist: str
    album: Optional[str] = None
    duration_ms: Optional[int] = None
    preview_url: Optional[str] = None
    album_art_url: Optional[str] = None
    spotify_id: Optional[str] = None

    class Config:
        from_attributes = True


def _to_song_out(song: Song) -> SongOut:
    return SongOut(
        song_id=song.id,
        title=song.title,
        artist=song.artist,
        album=song.album,
        duration_ms=song.duration_ms,
        preview_url=song.preview_url,
        album_art_url=song.album_art_url,
        spotify_id=song.spotify_id,
    )


@router.get("/search", response_model=List[SongOut])
async def search_songs(q: str = Query(..., min_length=2), limit: int = Query(20, ge=1, le=50), db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Song)
        .where(or_(Song.title.ilike(f"%{q}%"), Song.artist.ilike(f"%{q}%")))
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    # If local DB empty fallback to Spotify
    if not rows:
        try:
            spotify_results = await spotify_service.search_tracks(q, limit=limit)
        except Exception:
            return []
        return [
            SongOut(
                song_id=-1,  # indicates not persisted
                title=r["title"],
                artist=r["artist"],
                album=r.get("album"),
                duration_ms=r.get("duration_ms"),
                preview_url=r.get("preview_url"),
                album_art_url=r.get("album_art_url"),
                spotify_id=r.get("spotify_id"),
            )
            for r in spotify_results
        ]
    return [_to_song_out(s) for s in rows]


@router.get("/trending", response_model=List[SongOut])
async def trending_songs(limit: int = Query(20, ge=1, le=50), db: AsyncSession = Depends(get_db)):
    stmt = select(Song).order_by(Song.play_count.desc(), Song.id.asc()).limit(limit)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [_to_song_out(s) for s in rows]


@router.get("/{song_id}", response_model=SongOut)
async def get_song(song_id: int, db: AsyncSession = Depends(get_db)):
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return _to_song_out(song)
