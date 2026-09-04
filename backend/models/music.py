"""Music/Song models"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.core.database import Base

# Association table for song-genre many-to-many relationship
song_genre_association = Table(
    'song_genres',
    Base.metadata,
    Column('song_id', Integer, ForeignKey('songs.id')),
    Column('genre_id', Integer, ForeignKey('genres.id'))
)


class Song(Base):
    """Song model"""
    
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    artist = Column(String(255), nullable=False, index=True)
    album = Column(String(255))
    duration_ms = Column(Integer)  # Duration in milliseconds
    release_date = Column(DateTime)
    
    # External IDs
    spotify_id = Column(String(100), unique=True, index=True)
    youtube_id = Column(String(100))
    
    # Audio features (from Spotify or extracted)
    tempo = Column(Float)
    energy = Column(Float)  # 0.0 to 1.0
    danceability = Column(Float)  # 0.0 to 1.0
    valence = Column(Float)  # 0.0 to 1.0 (positivity)
    acousticness = Column(Float)  # 0.0 to 1.0
    instrumentalness = Column(Float)  # 0.0 to 1.0
    speechiness = Column(Float)  # 0.0 to 1.0
    loudness = Column(Float)  # In decibels
    
    # URLs
    preview_url = Column(String(500))
    album_art_url = Column(String(500))
    
    # Embeddings and metadata
    embedding_id = Column(String(100))  # ID in vector database
    lyrics = Column(Text)
    tags = Column(JSON, default=list)
    
    # Statistics
    play_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    genres = relationship("Genre", secondary=song_genre_association, back_populates="songs")
    liked_by = relationship("LikedSong", back_populates="song", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Song {self.title} by {self.artist}>"


class Genre(Base):
    """Genre model"""
    
    __tablename__ = "genres"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    parent_genre_id = Column(Integer, ForeignKey('genres.id'))
    
    # Relationships
    songs = relationship("Song", secondary=song_genre_association, back_populates="genres")
    parent = relationship("Genre", remote_side=[id])
    
    def __repr__(self):
        return f"<Genre {self.name}>"


class LikedSong(Base):
    """User's liked songs"""
    
    __tablename__ = "liked_songs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    song_id = Column(Integer, ForeignKey('songs.id'), nullable=False)
    liked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="liked_songs")
    song = relationship("Song", back_populates="liked_by")
    
    def __repr__(self):
        return f"<LikedSong user={self.user_id} song={self.song_id}>"
