"""Pytest configuration and fixtures"""

import asyncio
import os
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment variables before imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-characters-long"
os.environ["DEBUG"] = "True"
os.environ["ENVIRONMENT"] = "test"
os.environ["REQUIRE_CHROMA"] = "False"
os.environ["RATE_LIMIT_ENABLED"] = "False"

from api.main import app
from api.core.database import Base, get_db
from api.core.config import settings
from models.user import User
from models.music import Song, Genre
from models.playlist import Playlist


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def engine():
    """Create a test database engine"""
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield test_engine
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await test_engine.dispose()


@pytest.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session"""
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database session override"""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def demo_user(db_session: AsyncSession) -> User:
    """Create the demo user for testing"""
    from api.core.security import hash_password
    
    user = User(
        username="demo_user",
        email="demo@musigo.com",
        hashed_password=hash_password("demo_password"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def sample_songs(db_session: AsyncSession) -> list[Song]:
    """Create sample songs for testing"""
    songs = [
        Song(
            title="Bohemian Rhapsody",
            artist="Queen",
            album="A Night at the Opera",
            duration_ms=354000,
            spotify_id="7tFiyTwD0nx5a1eklYtX2J",
            tempo=144.0,
            energy=0.7,
            danceability=0.5,
            valence=0.5,
            play_count=1500,
            like_count=850,
        ),
        Song(
            title="Stairway to Heaven",
            artist="Led Zeppelin",
            album="Led Zeppelin IV",
            duration_ms=482000,
            spotify_id="5CQ30WqJwcep0pYcV4AMNc",
            tempo=84.0,
            energy=0.6,
            danceability=0.4,
            valence=0.4,
            play_count=1200,
            like_count=750,
        ),
        Song(
            title="Hotel California",
            artist="Eagles",
            album="Hotel California",
            duration_ms=391000,
            spotify_id="40riOy7x9W7GXjyGp4pjAv",
            tempo=147.0,
            energy=0.5,
            danceability=0.6,
            valence=0.3,
            play_count=800,
            like_count=600,
        ),
        Song(
            title="Imagine",
            artist="John Lennon",
            album="Imagine",
            duration_ms=183000,
            spotify_id="7pKfPomDEeI4TPT6EOYjn9",
            tempo=76.0,
            energy=0.3,
            danceability=0.5,
            valence=0.7,
            play_count=2000,
            like_count=1200,
        ),
        Song(
            title="Sweet Child O' Mine",
            artist="Guns N' Roses",
            album="Appetite for Destruction",
            duration_ms=356000,
            spotify_id="7o2CTH4ctstm8TNelqjb51",
            tempo=125.0,
            energy=0.9,
            danceability=0.6,
            valence=0.8,
            play_count=500,
            like_count=400,
        ),
    ]
    
    for song in songs:
        db_session.add(song)
    
    await db_session.commit()
    
    for song in songs:
        await db_session.refresh(song)
    
    return songs


@pytest.fixture
async def sample_genres(db_session: AsyncSession) -> list[Genre]:
    """Create sample genres for testing"""
    genres = [
        Genre(name="Rock", description="Rock music"),
        Genre(name="Pop", description="Pop music"),
        Genre(name="Jazz", description="Jazz music"),
        Genre(name="Classical", description="Classical music"),
        Genre(name="Electronic", description="Electronic music"),
    ]
    
    for genre in genres:
        db_session.add(genre)
    
    await db_session.commit()
    
    for genre in genres:
        await db_session.refresh(genre)
    
    return genres


@pytest.fixture
async def sample_playlist(db_session: AsyncSession, demo_user: User, sample_songs: list[Song]) -> Playlist:
    """Create a sample playlist for testing
    
    Note: Creates playlist for 'demo' API user (not demo_user fixture) to match public access mode.
    """
    # Get or create the "demo" user that the API uses
    from sqlalchemy import select
    stmt = select(User).where(User.username == "demo")
    result = await db_session.execute(stmt)
    api_demo_user = result.scalar_one_or_none()
    
    if not api_demo_user:
        from api.core.security import hash_password
        api_demo_user = User(
            username="demo",
            email="demo@example.com",
            hashed_password=hash_password("demo123"),
            is_active=True,
        )
        db_session.add(api_demo_user)
        await db_session.commit()
        await db_session.refresh(api_demo_user)
    
    playlist = Playlist(
        name="My Test Playlist",
        description="A playlist for testing",
        user_id=api_demo_user.id,  # Use API's demo user
        is_public=True,
    )
    db_session.add(playlist)
    await db_session.commit()
    await db_session.refresh(playlist)
    
    # Add some songs to the playlist
    from sqlalchemy import insert
    from models.playlist import playlist_song_association
    
    for idx, song in enumerate(sample_songs[:3]):
        stmt = insert(playlist_song_association).values(
            playlist_id=playlist.id,
            song_id=song.id,
            position=idx,
        )
        await db_session.execute(stmt)
    
    await db_session.commit()
    await db_session.refresh(playlist)
    
    return playlist


@pytest.fixture
def auth_headers(demo_user: User) -> dict:
    """Create authentication headers for testing"""
    from api.core.security import create_access_token
    
    token = create_access_token(data={"sub": demo_user.username})
    return {"Authorization": f"Bearer {token}"}
