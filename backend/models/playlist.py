"""Playlist model"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.core.database import Base

# Association table for playlist-song many-to-many relationship
playlist_song_association = Table(
    'playlist_songs',
    Base.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id')),
    Column('song_id', Integer, ForeignKey('songs.id')),
    Column('position', Integer),  # Order of songs in playlist
    Column('added_at', DateTime(timezone=True), server_default=func.now())
)


class Playlist(Base):
    """Playlist model"""
    
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Playlist properties
    is_public = Column(Boolean, default=False)
    is_collaborative = Column(Boolean, default=False)
    cover_image_url = Column(String(500))
    
    # Statistics
    follower_count = Column(Integer, default=0)
    total_duration_ms = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="playlists")
    songs = relationship("Song", secondary=playlist_song_association)
    
    def __repr__(self):
        return f"<Playlist {self.name} by user {self.user_id}>"
