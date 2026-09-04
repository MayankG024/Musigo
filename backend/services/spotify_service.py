"""Spotify service integration (catalog & metadata fetching)

This module provides async wrappers around spotipy for:
 - Searching tracks to enrich local DB
 - Fetching audio features
 - Fetching artist & genre metadata

Note: spotipy is synchronous. For now we delegate to threadpool via anyio.to_thread.run_sync.
Later we can replace with an async-native client if needed.
"""

from typing import List, Dict, Any, Optional
import os
import anyio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

_client: Optional[spotipy.Spotify] = None


def _get_client() -> spotipy.Spotify:
    global _client
    if _client is None:
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise RuntimeError("Missing SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET env vars")
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        _client = spotipy.Spotify(auth_manager=auth_manager)
    return _client


async def search_tracks(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    def _call():
        return _get_client().search(q=query, type="track", limit=limit)
    data = await anyio.to_thread.run_sync(_call)
    items = data.get("tracks", {}).get("items", [])
    results: List[Dict[str, Any]] = []
    for t in items:
        results.append({
            "spotify_id": t.get("id"),
            "title": t.get("name"),
            "artist": ", ".join(a.get("name") for a in t.get("artists", [])),
            "album": t.get("album", {}).get("name"),
            "preview_url": t.get("preview_url"),
            "album_art_url": (t.get("album", {}).get("images") or [{}])[0].get("url"),
            "duration_ms": t.get("duration_ms"),
            "raw": t,
        })
    return results


async def get_audio_features(spotify_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    if not spotify_ids:
        return {}
    def _call():
        return _get_client().audio_features(tracks=spotify_ids)
    features_list = await anyio.to_thread.run_sync(_call)
    mapping: Dict[str, Dict[str, Any]] = {}
    for f in features_list or []:
        if not f:
            continue
        mapping[f.get("id")] = f
    return mapping
