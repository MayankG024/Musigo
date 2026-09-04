"""Favorites (Liked songs) endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Any
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from api.core.database import get_db
from models.music import LikedSong, Song
from api.routers.auth import get_current_user

router = APIRouter(prefix="/favorites", tags=["favorites"])  # mounted under /api/user


class SongOut(BaseModel):
    song_id: int
    title: str
    artist: str
    album: str | None = None
    album_art_url: str | None = None
    preview_url: str | None = None
    spotify_id: str | None = None


class FavoriteItem(BaseModel):
    id: int
    user_id: int
    song_id: int
    song: SongOut
    created_at: str | None = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int


@router.get("/", response_model=PaginatedResponse)
async def list_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    # total count
    count_stmt = select(func.count()).select_from(LikedSong).where(LikedSong.user_id == user.id)
    count_res = await db.execute(count_stmt)
    total = count_res.scalar_one()

    # page slice
    stmt = (
        select(LikedSong, Song)
        .join(Song, LikedSong.song_id == Song.id)
        .where(LikedSong.user_id == user.id)
        .order_by(LikedSong.liked_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    rows = result.all()
    items: List[FavoriteItem] = []
    for liked, song in rows:
        items.append(
            FavoriteItem(
                id=liked.id,
                user_id=liked.user_id,
                song_id=song.id,
                song=SongOut(
                    song_id=song.id,
                    title=song.title,
                    artist=song.artist,
                    album=song.album,
                    album_art_url=song.album_art_url,
                    preview_url=song.preview_url,
                    spotify_id=song.spotify_id,
                ),
                created_at=str(liked.liked_at) if liked.liked_at else None,
            )
        )
    pages = max(1, (total + page_size - 1) // page_size)
    return PaginatedResponse(items=[i.model_dump() for i in items], total=total, page=page, page_size=page_size, pages=pages)


@router.post("/{song_id}", status_code=201, response_model=FavoriteItem)
async def like_song(song_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    # Check existing like
    stmt = select(LikedSong).where(and_(LikedSong.user_id == user.id, LikedSong.song_id == song_id))
    res = await db.execute(stmt)
    liked_obj = res.scalar_one_or_none()
    if liked_obj:
        # Idempotent; reuse existing like object and fall through to formatted return
        pass
    else:
        liked_obj = LikedSong(user_id=user.id, song_id=song_id)
        db.add(liked_obj)
        # increment like_count
        song.like_count = (song.like_count or 0) + 1
        db.add(song)
        await db.commit()
        await db.refresh(liked_obj)
        await db.refresh(song)
    return FavoriteItem(
        id=liked_obj.id,
        user_id=liked_obj.user_id,
        song_id=song.id,
        song=SongOut(
            song_id=song.id,
            title=song.title,
            artist=song.artist,
            album=song.album,
            album_art_url=song.album_art_url,
            preview_url=song.preview_url,
            spotify_id=song.spotify_id,
        ),
        created_at=str(liked_obj.liked_at) if liked_obj.liked_at else None,
    )


@router.delete("/{song_id}", status_code=204)
async def unlike_song(song_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    stmt = select(LikedSong).where(and_(LikedSong.user_id == user.id, LikedSong.song_id == song_id))
    res = await db.execute(stmt)
    liked = res.scalar_one_or_none()
    if not liked:
        return None
    await db.delete(liked)
    # decrement like_count safely
    if song.like_count and song.like_count > 0:
        song.like_count -= 1
        db.add(song)
    await db.commit()
    return None


class FavoriteCheck(BaseModel):
    song_id: int
    liked: bool


@router.get("/{song_id}/check", response_model=FavoriteCheck)
async def check_favorite(song_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    stmt = select(func.count()).select_from(LikedSong).where(and_(LikedSong.user_id == user.id, LikedSong.song_id == song_id))
    result = await db.execute(stmt)
    count = result.scalar_one()
    if count > 0:
        return FavoriteCheck(song_id=song_id, liked=True)
    # Frontend expects a 404 when not liked (uses try/catch to return false)
    raise HTTPException(status_code=404, detail="Not liked")
