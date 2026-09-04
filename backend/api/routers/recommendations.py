"""Compatibility router for recommendations paths used by frontend"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from rag_system import vector_store

router = APIRouter(tags=["recommendations"])  # will be mounted under /api


class RecommendationRequest(BaseModel):
    seed_songs: Optional[List[str]] = None
    seed_artists: Optional[List[str]] = None
    seed_genres: Optional[List[str]] = None
    limit: int = 10
    # audio_features payload can be added later; ignored for now


@router.post("/recommendations/recommend")
async def recommendations_recommend(body: RecommendationRequest | List[str]):
    """
    Accepts either the frontend's object shape { seed_songs, limit, ... } or a raw
    list of song ids for backward compatibility.
    """
    try:
        if isinstance(body, list):
            song_ids = body
            limit = 10
        else:
            song_ids = body.seed_songs or []
            limit = body.limit
        if not song_ids:
            # No seed songs provided; return empty recommendations for now
            return []
        return await vector_store.get_recommendations(song_ids=song_ids, n_recommendations=limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {e}")
