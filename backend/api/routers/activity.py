"""User activity endpoints: search history & recently played"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from api.core.database import get_db
from api.routers.auth import get_current_user
from models.music import Song

router = APIRouter(prefix="/activity", tags=["activity"])  # mounted under /api/user

# We'll store search history in the user's music_preferences JSON for simplicity or create new field?
# For now embed two arrays inside music_preferences: { search_history: [...], recently_played: [...] }
# If absent, create structure.

MAX_SEARCH_HISTORY = 50
MAX_RECENTLY_PLAYED = 100


class SearchEntry(BaseModel):
    query: str
    timestamp: str

class RecentlyPlayedEntry(BaseModel):
    song_id: int
    title: str
    artist: str
    played_at: str

class SearchHistoryOut(BaseModel):
    items: List[SearchEntry]

class RecentlyPlayedOut(BaseModel):
    items: List[RecentlyPlayedEntry]

class LogSearchPayload(BaseModel):
    query: str


@router.post("/search", response_model=SearchEntry, status_code=201)
async def log_search(payload: LogSearchPayload, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    if not payload.query or len(payload.query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
    prefs = user.music_preferences or {}
    history = prefs.get("search_history", [])
    entry = {"query": payload.query.strip(), "timestamp": datetime.now(timezone.utc).isoformat()}
    history.insert(0, entry)
    history = history[:MAX_SEARCH_HISTORY]
    prefs["search_history"] = history
    user.music_preferences = prefs
    db.add(user)
    await db.commit()
    return SearchEntry(**entry)


@router.get("/search", response_model=SearchHistoryOut)
async def get_search_history(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    prefs = user.music_preferences or {}
    history = prefs.get("search_history", [])
    return SearchHistoryOut(items=[SearchEntry(**h) for h in history])


class LogPlayPayload(BaseModel):
    song_id: int


@router.post("/recently-played", response_model=RecentlyPlayedEntry, status_code=201)
async def log_recently_played(payload: LogPlayPayload, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    song = await db.get(Song, payload.song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    prefs = user.music_preferences or {}
    recent = prefs.get("recently_played", [])
    entry = {
        "song_id": song.id,
        "title": song.title,
        "artist": song.artist,
        "played_at": datetime.now(timezone.utc).isoformat(),
    }
    # Remove existing duplicate entries of same song id
    recent = [r for r in recent if r.get("song_id") != song.id]
    recent.insert(0, entry)
    recent = recent[:MAX_RECENTLY_PLAYED]
    prefs["recently_played"] = recent
    user.music_preferences = prefs
    db.add(user)
    await db.commit()
    return RecentlyPlayedEntry(**entry)


@router.get("/recently-played", response_model=RecentlyPlayedOut)
async def get_recently_played(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    prefs = user.music_preferences or {}
    recent = prefs.get("recently_played", [])
    return RecentlyPlayedOut(items=[RecentlyPlayedEntry(**r) for r in recent])
