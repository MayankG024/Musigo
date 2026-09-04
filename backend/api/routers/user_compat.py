"""Compatibility endpoints under /api/user to match frontend expectations.

Provides:
- GET /api/user/history (paginated)
- DELETE /api/user/history
- GET /api/user/recently-played (list of songs)
- POST /api/user/recently-played/{song_id}
- GET /api/user/stats
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Any
from math import ceil
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.core.database import get_db
from api.routers.auth import get_current_user
from models.user import User
from models.music import Song, LikedSong


router = APIRouter(prefix="", tags=["user-compat"])  # mounted under /api/user in main


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int


class SearchHistoryItem(BaseModel):
    id: str
    user_id: int
    query: str
    results_count: int
    created_at: str


@router.get("/history", response_model=PaginatedResponse)
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    prefs = user.music_preferences or {}
    history = prefs.get("search_history", [])  # list of { query, timestamp }
    total = len(history)
    pages = max(1, ceil(total / page_size)) if total else 1
    start = (page - 1) * page_size
    end = start + page_size
    slice_items = history[start:end]
    items = [
        SearchHistoryItem(
            id=str(idx + 1 + start),
            user_id=user.id,
            query=entry.get("query", ""),
            results_count=0,
            created_at=entry.get("timestamp", ""),
        ).model_dump()
        for idx, entry in enumerate(slice_items)
    ]
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)


@router.delete("/history", status_code=204)
async def clear_history(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    prefs = user.music_preferences or {}
    prefs["search_history"] = []
    user.music_preferences = prefs
    db.add(user)
    await db.commit()
    return None


class SongOut(BaseModel):
    song_id: int
    title: str
    artist: str
    album: str | None = None
    duration_ms: int | None = None
    preview_url: str | None = None
    album_art_url: str | None = None
    spotify_id: str | None = None


@router.get("/recently-played", response_model=List[SongOut])
async def get_recently_played(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    prefs = user.music_preferences or {}
    recent = prefs.get("recently_played", [])  # list of { song_id, ... }
    ids = [r.get("song_id") for r in recent][:limit]
    if not ids:
        return []
    # Fetch songs preserving order
    stmt = select(Song).where(Song.id.in_(ids))
    res = await db.execute(stmt)
    song_map = {s.id: s for s in res.scalars().all()}
    out: List[SongOut] = []
    for sid in ids:
        s = song_map.get(sid)
        if not s:
            continue
        out.append(
            SongOut(
                song_id=s.id,
                title=s.title,
                artist=s.artist,
                album=s.album,
                duration_ms=s.duration_ms,
                preview_url=s.preview_url,
                album_art_url=s.album_art_url,
                spotify_id=s.spotify_id,
            )
        )
    return out


@router.post("/recently-played/{song_id}", status_code=201)
async def add_recently_played(
    song_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # emulate activity.log_recently_played but with path param
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    from datetime import datetime, timezone
    prefs = user.music_preferences or {}
    recent = prefs.get("recently_played", [])
    entry = {
        "song_id": song.id,
        "title": song.title,
        "artist": song.artist,
        "played_at": datetime.now(timezone.utc).isoformat(),
    }
    recent = [r for r in recent if r.get("song_id") != song.id]
    recent.insert(0, entry)
    recent = recent[:100]
    prefs["recently_played"] = recent
    user.music_preferences = prefs
    db.add(user)
    await db.commit()
    return {"detail": "added"}


@router.get("/stats")
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # favorites count
    fav_stmt = select(LikedSong).where(LikedSong.user_id == user.id)
    fav_res = await db.execute(fav_stmt)
    favorites = fav_res.scalars().all()
    favorites_count = len(favorites)

    # playlists count
    from models.playlist import Playlist
    pl_stmt = select(Playlist).where(Playlist.user_id == user.id)
    pl_res = await db.execute(pl_stmt)
    playlists_count = len(pl_res.scalars().all())

    # total listening time estimate from recently played durations
    prefs = user.music_preferences or {}
    recent = prefs.get("recently_played", [])
    ids = [r.get("song_id") for r in recent]
    total_listening_time = 0
    if ids:
        stmt = select(Song).where(Song.id.in_(ids))
        res = await db.execute(stmt)
        for s in res.scalars().all():
            total_listening_time += (s.duration_ms or 0)

    # simple top artists/genres from likes
    from collections import Counter
    artist_counts = Counter()
    genre_counts = Counter()
    if favorites:
        song_ids = [f.song_id for f in favorites]
        sres = await db.execute(select(Song).where(Song.id.in_(song_ids)))
        for s in sres.scalars().all():
            if s.artist:
                artist_counts[s.artist] += 1
            for g in (s.genres or []):
                genre_counts[g] += 1

    return {
        "favorites_count": favorites_count,
        "playlists_count": playlists_count,
        "total_listening_time": total_listening_time,
        "top_genres": [g for g, _ in genre_counts.most_common(5)],
        "top_artists": [a for a, _ in artist_counts.most_common(5)],
    }
