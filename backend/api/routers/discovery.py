"""Music discovery endpoints using RAG"""

from fastapi import APIRouter, Query, HTTPException, Request
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from rag_system import vector_store
from worker import enqueue_embedding
from services import spotify_service
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from api.core.database import get_db
from api.core.rate_limit import limiter
from models.music import Song, Genre

router = APIRouter()


class DiscoveryQuery(BaseModel):
    query: str
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None


class DiscoveryResult(BaseModel):
    song_id: str
    title: str
    artist: str
    similarity_score: float
    metadata: Dict[str, Any]


@router.post("/discover", response_model=List[DiscoveryResult])
@limiter.limit("10/minute")
async def discover_music(request: Request, query: DiscoveryQuery):
    """Discover music using natural language queries"""
    results = await vector_store.search_similar(
        query=query.query,
        n_results=query.limit,
        filter_dict=query.filters
    )
    
    # Format results
    discovery_results = []
    for result in results:
        metadata = result.get("metadata", {})
        discovery_results.append(
            DiscoveryResult(
                song_id=result["id"],
                title=metadata.get("title", "Unknown"),
                artist=metadata.get("artist", "Unknown"),
                similarity_score=1.0 - result.get("distance", 0),
                metadata=metadata
            )
        )
    
    return discovery_results


@router.post("/recommend")
@limiter.limit("10/minute")
async def get_recommendations(request: Request, song_ids: List[str], limit: int = Query(10, ge=1, le=50)):
    """Get recommendations based on multiple songs (vector store)."""
    try:
        recommendations = await vector_store.get_recommendations(song_ids=song_ids, n_recommendations=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {e}")
    return recommendations


@router.post("/recommendations/recommend")
async def get_recommendations_alias(song_ids: List[str], limit: int = Query(10, ge=1, le=50)):
    """Alias path matching frontend expectation (/recommendations/recommend)."""
    # NOTE: do not call get_recommendations() directly — its slowapi limiter
    # wrapper requires a Response param and fails when invoked as a plain function.
    try:
        return await vector_store.get_recommendations(song_ids=song_ids, n_recommendations=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {e}")


@router.get("/spotify/search", summary="Search Spotify directly")
@limiter.limit("20/minute")
async def spotify_search(request: Request, q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=50)):
    results = await spotify_service.search_tracks(q, limit=limit)
    return {"items": results, "count": len(results)}


# Supplemental endpoints
class SimpleSong(BaseModel):
    song_id: int
    title: str
    artist: str
    play_count: int | None = None
    like_count: int | None = None
    album_art_url: str | None = None
    spotify_id: str | None = None
    class Config:
        from_attributes = True


@router.get("/trending", response_model=List[SimpleSong])
async def discovery_trending(limit: int = Query(20, ge=1, le=50), db: AsyncSession = Depends(get_db)):
    stmt = select(Song).order_by(Song.play_count.desc(), Song.like_count.desc()).limit(limit)
    result = await db.execute(stmt)
    songs = result.scalars().all()
    return [
        SimpleSong(
            song_id=s.id,
            title=s.title,
            artist=s.artist,
            play_count=s.play_count,
            like_count=s.like_count,
            album_art_url=s.album_art_url,
            spotify_id=s.spotify_id,
        )
        for s in songs
    ]


class GenreOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    song_count: int
    class Config:
        from_attributes = True


@router.get("/genres", response_model=List[str])
async def list_genres(limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    # Count songs per genre
    stmt = select(Genre, func.count(Song.id)).join(Genre.songs, isouter=True).group_by(Genre.id).order_by(func.count(Song.id).desc()).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()
    names: List[str] = []
    for genre, count in rows:
        names.append(genre.name)
    return names


class SongOut(BaseModel):
    song_id: int
    title: str
    artist: str
    album: str | None = None
    duration_ms: int | None = None
    preview_url: str | None = None
    album_art_url: str | None = None
    spotify_id: str | None = None
    class Config:
        from_attributes = True


@router.get("/similar/{song_id}", response_model=List[SongOut])
async def similar_songs(song_id: int, limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)):
    song = await db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    base_id = song.embedding_id or song.spotify_id
    if not base_id:
        raise HTTPException(status_code=400, detail="Song has no embedding reference")
    try:
        recs = await vector_store.get_recommendations(song_ids=[base_id], n_recommendations=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity failed: {e}")
    # Map vector IDs back to songs
    ids = []
    for r in recs:
        rid = r.get("id")
        if not rid:
            continue
        try:
            ids.append(int(str(rid)))
        except ValueError:
            # If not numeric, try matching embedding_id later
            pass
    songs_map = {}
    if ids:
        res = await db.execute(select(Song).where(Song.id.in_(ids)))
        songs_map.update({s.id: s for s in res.scalars().all()})
    # Also try by embedding_id for non-numeric ids
    embed_ids = [str(r.get("id")) for r in recs if str(r.get("id")).isdigit() is False]
    if embed_ids:
        res2 = await db.execute(select(Song).where(Song.embedding_id.in_(embed_ids)))
        for s in res2.scalars().all():
            songs_map[s.id] = s
    out: List[SongOut] = []
    for r in recs:
        s = None
        rid = r.get("id")
        # Prefer numeric ID match
        try:
            s = songs_map.get(int(str(rid)))
        except Exception:
            s = None
        # Fallback by embedding_id
        if not s:
            # linear search small set
            for v in songs_map.values():
                if v.embedding_id and str(v.embedding_id) == str(rid):
                    s = v
                    break
        if not s:
            continue
        out.append(SongOut(
            song_id=s.id,
            title=s.title,
            artist=s.artist,
            album=s.album,
            duration_ms=s.duration_ms,
            preview_url=s.preview_url,
            album_art_url=s.album_art_url,
            spotify_id=s.spotify_id,
        ))
    return out


# --- Ingestion & Demo Seed ---
class IndexedItem(BaseModel):
    song_id: int
    title: str
    artist: str
    spotify_id: str | None = None
    class Config:
        from_attributes = True


@router.post("/index/spotify", response_model=List[IndexedItem], summary="Index tracks from Spotify into DB and vector store")
async def index_from_spotify(q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)):
    try:
        tracks = await spotify_service.search_tracks(q, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spotify search failed: {e}")
    indexed: List[IndexedItem] = []
    for t in tracks:
        # Skip if already exists by spotify_id
        if t.get("spotify_id"):
            existing = await db.execute(select(Song).where(Song.spotify_id == t["spotify_id"]))
            if existing.scalar_one_or_none():
                continue
        song = Song(
            title=t.get("title") or "",
            artist=t.get("artist") or "",
            album=t.get("album"),
            duration_ms=t.get("duration_ms"),
            preview_url=t.get("preview_url"),
            album_art_url=t.get("album_art_url"),
            spotify_id=t.get("spotify_id"),
        )
        db.add(song)
        await db.flush()
        # Try to add to vector store (best-effort)
        try:
            enqueue_embedding(song_id=str(song.spotify_id or song.id), song_data={
                "title": song.title,
                "artist": song.artist,
                "album": song.album or "",
                "genres": [],
                "tags": [],
                "energy": 0.5,
                "valence": 0.5,
                "danceability": 0.5,
            })
            song.embedding_id = song.spotify_id or str(song.id)
        except Exception:
            # Embeddings optional; ignore failures
            pass
        indexed.append(IndexedItem(song_id=song.id, title=song.title, artist=song.artist, spotify_id=song.spotify_id))
    await db.commit()
    return indexed


@router.post("/seed/demo", response_model=List[IndexedItem], summary="Seed a few demo songs without Spotify")
async def seed_demo(db: AsyncSession = Depends(get_db)):
    demo = [
        {"title": "Demo Breeze", "artist": "LoFi Collective"},
        {"title": "Neon Nights", "artist": "Synth Wave"},
        {"title": "Sunset Drive", "artist": "Chill Masters"},
        {"title": "Midnight Jazz", "artist": "City Quartet"},
        {"title": "Ocean Echoes", "artist": "Ambient Dreams"},
    ]
    created: List[IndexedItem] = []
    for item in demo:
        song = Song(title=item["title"], artist=item["artist"]) 
        db.add(song)
        await db.flush()
        try:
            await vector_store.add_song(song_id=str(song.id), song_data={
                "title": song.title,
                "artist": song.artist,
                "album": "",
                "genres": [],
                "tags": [],
                "energy": 0.5,
                "valence": 0.5,
                "danceability": 0.5,
            })
            song.embedding_id = str(song.id)
        except Exception:
            pass
        created.append(IndexedItem(song_id=song.id, title=song.title, artist=song.artist, spotify_id=None))
    await db.commit()
    return created


@router.post("/index/all", response_model=List[IndexedItem], summary="(Re)index all songs into the vector store")
async def index_all(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Song))
    songs = res.scalars().all()
    indexed: List[IndexedItem] = []
    for s in songs:
        try:
            enqueue_embedding(song_id=str(s.spotify_id or s.id), song_data={
                "title": s.title,
                "artist": s.artist,
                "album": s.album or "",
                "genres": [],
                "tags": [],
                "energy": 0.5,
                "valence": 0.5,
                "danceability": 0.5,
            })
            s.embedding_id = s.spotify_id or str(s.id)
            indexed.append(IndexedItem(song_id=s.id, title=s.title, artist=s.artist, spotify_id=s.spotify_id))
        except Exception:
            # ignore individual failures
            pass
    db.add_all(songs)
    await db.commit()
    return indexed
