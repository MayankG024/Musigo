"""Tests for music endpoints"""

import pytest
from httpx import AsyncClient
from models.music import Song


@pytest.mark.asyncio
class TestMusicEndpoints:
    """Test music-related endpoints"""
    
    async def test_search_songs(self, client: AsyncClient, sample_songs: list[Song]):
        """Test song search functionality"""
        # Search by title - note: parameter is 'q' not 'query'
        response = await client.get("/api/music/search?q=bohemian")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        assert any(song["title"] == "Bohemian Rhapsody" for song in data)
    
    async def test_search_by_artist(self, client: AsyncClient, sample_songs: list[Song]):
        """Test search by artist name"""
        response = await client.get("/api/music/search?q=queen")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        assert any(song["artist"] == "Queen" for song in data)
    
    async def test_search_by_album(self, client: AsyncClient, sample_songs: list[Song]):
        """Test search by album name"""
        response = await client.get("/api/music/search?q=imagine")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
    
    async def test_search_no_results(self, client: AsyncClient, sample_songs: list[Song]):
        """Test search with no results"""
        response = await client.get("/api/music/search?q=nonexistentsong12345")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 0
    
    async def test_get_trending_songs(self, client: AsyncClient, sample_songs: list[Song]):
        """Test trending songs endpoint"""
        response = await client.get("/api/music/trending")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        # SongResponse doesn't include play_count, so just verify ordering
        # First song should be "Imagine" based on play_count in fixture
        assert data[0]["title"] == "Imagine"
        assert data[0]["artist"] == "John Lennon"
    
    async def test_get_trending_with_limit(self, client: AsyncClient, sample_songs: list[Song]):
        """Test trending songs with limit parameter"""
        response = await client.get("/api/music/trending?limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
    
    async def test_get_song_by_id(self, client: AsyncClient, sample_songs: list[Song]):
        """Test getting a specific song by ID"""
        song_id = sample_songs[0].id
        response = await client.get(f"/api/songs/{song_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["song_id"] == song_id  # Note: API returns 'song_id' not 'id'
        assert data["title"] == sample_songs[0].title
        assert data["artist"] == sample_songs[0].artist
    
    async def test_get_song_not_found(self, client: AsyncClient):
        """Test getting a non-existent song"""
        response = await client.get("/api/songs/99999")
        assert response.status_code == 404
    
    async def test_list_songs(self, client: AsyncClient, sample_songs: list[Song]):
        """Test listing all songs"""
        # Use /api/songs/trending to list songs (there's no plain list endpoint)
        response = await client.get("/api/songs/trending?limit=50")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= len(sample_songs)
    
    async def test_list_songs_pagination(self, client: AsyncClient, sample_songs: list[Song]):
        """Test song listing with pagination"""
        # Get limited results
        response = await client.get("/api/songs/trending?limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
