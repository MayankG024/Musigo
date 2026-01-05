"""Playlist endpoints (CRUD + song management)"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from api.core.database import get_db
from api.core.rate_limit import limiter
from models.playlist import Playlist, playlist_song_association
from models.music import Song
from api.routers.auth import get_current_user

router = APIRouter(prefix="")  # prefix applied in main include


class PlaylistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False


class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class PlaylistOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    song_count: int
    is_public: bool
    user_id: int

    class Config:
        from_attributes = True


async def _playlist_to_out(db: AsyncSession, pl: Playlist) -> PlaylistOut:
    # Count songs (association table)
    count_stmt = select(func.count()).select_from(playlist_song_association).where(playlist_song_association.c.playlist_id == pl.id)
    result = await db.execute(count_stmt)
    song_count = result.scalar_one()
    return PlaylistOut(
        id=pl.id,
        name=pl.name,
        description=pl.description,
        song_count=song_count,
        is_public=pl.is_public,
        user_id=pl.user_id,
    )


@router.post("/", response_model=PlaylistOut, status_code=201)
@limiter.limit("30/minute")
async def create_playlist(request: Request, payload: PlaylistCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    pl = Playlist(name=payload.name, description=payload.description, is_public=payload.is_public, user_id=user.id)
    db.add(pl)
    await db.commit()
    await db.refresh(pl)
    return await _playlist_to_out(db, pl)


@router.get("/my", response_model=List[PlaylistOut])
@limiter.limit("100/minute")
async def list_my_playlists(request: Request, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    stmt = select(Playlist).where(Playlist.user_id == user.id).order_by(Playlist.created_at.desc())
    result = await db.execute(stmt)
    playlists = result.scalars().all()
    return [await _playlist_to_out(db, p) for p in playlists]


@router.get("/public", response_model=List[PlaylistOut])
async def list_public_playlists(limit: int = Query(50, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    stmt = select(Playlist).where(Playlist.is_public == True).order_by(Playlist.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    playlists = result.scalars().all()
    return [await _playlist_to_out(db, p) for p in playlists]


@router.get("/{playlist_id}", response_model=PlaylistOut)
async def get_playlist(playlist_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    pl = await db.get(Playlist, playlist_id)
    if not pl or (not pl.is_public and pl.user_id != user.id):
        raise HTTPException(status_code=404, detail="Playlist not found")
    return await _playlist_to_out(db, pl)


@router.patch("/{playlist_id}", response_model=PlaylistOut)
async def update_playlist(playlist_id: int, payload: PlaylistUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    pl = await db.get(Playlist, playlist_id)
    if not pl or pl.user_id != user.id:
        raise HTTPException(status_code=404, detail="Playlist not found")
    changed = False
    for field in ["name", "description", "is_public"]:
        val = getattr(payload, field)
        if val is not None:
            setattr(pl, field, val)
            changed = True
    if changed:
        db.add(pl)
        await db.commit()
        await db.refresh(pl)
    return await _playlist_to_out(db, pl)


@router.delete("/{playlist_id}", status_code=204)
async def delete_playlist(playlist_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    pl = await db.get(Playlist, playlist_id)
    if not pl or pl.user_id != user.id:
        raise HTTPException(status_code=404, detail="Playlist not found")
    await db.delete(pl)
    await db.commit()
    return None


class ReorderPayload(BaseModel):
    song_ids: List[int]


@router.put("/{playlist_id}/reorder", response_model=PlaylistOut)
async def reorder_playlist(playlist_id: int, payload: ReorderPayload, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    """Reorder songs in a playlist by providing the new song_id order"""
    pl = await db.get(Playlist, playlist_id)
    if not pl or pl.user_id != user.id:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    # Delete existing associations for this playlist
    await db.execute(
        delete(playlist_song_association).where(
            playlist_song_association.c.playlist_id == playlist_id
        )
    )
    
    # Re-insert with new positions
    for position, song_id in enumerate(payload.song_ids):
        # Verify song exists
        song = await db.get(Song, song_id)
        if not song:
            raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
        
        await db.execute(
            playlist_song_association.insert().values(
                playlist_id=playlist_id,
                song_id=song_id,
                position=position
            )
        )
    
    await db.commit()
    await db.refresh(pl)
    return await _playlist_to_out(db, pl)


@router.post("/{playlist_id}/songs/{song_id}", response_model=PlaylistOut)
async def add_song_to_playlist(playlist_id: int, song_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    """Add a song to the end of a playlist"""
    pl = await db.get(Playlist, playlist_id)
    if not pl or pl.user_id != user.id:
        raise HTTPException(status_code=404, detail="Playlist not found")
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Check if song already exists in playlist
    check_stmt = select(playlist_song_association).where(
        (playlist_song_association.c.playlist_id == playlist_id) &
        (playlist_song_association.c.song_id == song_id)
    )
    existing = await db.execute(check_stmt)
    if existing.scalar_one_or_none():
        return await _playlist_to_out(db, pl)  # Already exists
    
    # Get max position
    max_pos_stmt = select(func.max(playlist_song_association.c.position)).where(
        playlist_song_association.c.playlist_id == playlist_id
    )
    result = await db.execute(max_pos_stmt)
    max_pos = result.scalar_one_or_none() or -1
    
    # Add song with next position
    await db.execute(
        playlist_song_association.insert().values(
            playlist_id=playlist_id,
            song_id=song_id,
            position=max_pos + 1
        )
    )
    await db.commit()
    await db.refresh(pl)
    return await _playlist_to_out(db, pl)


@router.delete("/{playlist_id}/songs/{song_id}", response_model=PlaylistOut)
async def remove_song_from_playlist(playlist_id: int, song_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    pl = await db.get(Playlist, playlist_id)
    if not pl or pl.user_id != user.id:
        raise HTTPException(status_code=404, detail="Playlist not found")
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    if song in pl.songs:
        pl.songs.remove(song)
        db.add(pl)
        await db.commit()
        await db.refresh(pl)
    return await _playlist_to_out(db, pl)


class SongInPlaylist(BaseModel):
    id: int
    title: str
    artist: str
    album: Optional[str]
    duration_ms: Optional[int]
    preview_url: Optional[str]
    album_art_url: Optional[str]
    position: int
    
    class Config:
        from_attributes = True


@router.get("/{playlist_id}/songs", response_model=List[SongInPlaylist])
async def list_playlist_songs(playlist_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    """Get all songs in a playlist in the correct order"""
    pl = await db.get(Playlist, playlist_id)
    if not pl or (not pl.is_public and pl.user_id != user.id):
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    # Query songs with position from association table
    stmt = (
        select(Song, playlist_song_association.c.position)
        .join(playlist_song_association, Song.id == playlist_song_association.c.song_id)
        .where(playlist_song_association.c.playlist_id == playlist_id)
        .order_by(playlist_song_association.c.position)
    )
    result = await db.execute(stmt)
    songs_with_position = result.all()
    
    return [
        SongInPlaylist(
            id=song.id,
            title=song.title,
            artist=song.artist,
            album=song.album,
            duration_ms=song.duration_ms,
            preview_url=song.preview_url,
            album_art_url=song.album_art_url,
            position=position
        )
        for song, position in songs_with_position
    ]
    class _Song(BaseModel):
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
    return [
        _Song(
            song_id=s.id,
            title=s.title,
            artist=s.artist,
            album=s.album,
            duration_ms=s.duration_ms,
            preview_url=s.preview_url,
            album_art_url=s.album_art_url,
            spotify_id=s.spotify_id,
        ) for s in pl.songs
    ]
