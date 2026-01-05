"""add_performance_indexes

Add indexes for frequently queried columns to improve performance:
- Songs: search queries (title, artist, album), ordering (play_count, like_count)
- Playlists: user lookup, ordering (created_at)
- Playlist associations: ordering songs by position
- Liked songs: user lookups
- Genres: name lookups
"""

revision = '0d4b7da9f023'
down_revision = 'f67b011b6b46'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Add performance indexes"""
    
    # Songs table indexes
    # Note: id, title, artist, spotify_id already have indexes from model definition
    # Adding composite indexes for common query patterns
    
    # Index for trending songs (ORDER BY play_count DESC, like_count DESC)
    op.create_index(
        'idx_songs_trending',
        'songs',
        ['play_count', 'like_count'],
        postgresql_using='btree'
    )
    
    # Index for album-based queries
    op.create_index(
        'idx_songs_album',
        'songs',
        ['album'],
        postgresql_using='btree'
    )
    
    # Index for release date queries (newest first)
    op.create_index(
        'idx_songs_release_date',
        'songs',
        ['release_date'],
        postgresql_using='btree'
    )
    
    # Index for created_at (recently added songs)
    op.create_index(
        'idx_songs_created_at',
        'songs',
        ['created_at'],
        postgresql_using='btree'
    )
    
    # Playlists table indexes
    # Note: id already has index from model definition
    
    # Index for user playlists lookup (user_id already indexed in model)
    # Adding composite index for user playlists ordered by creation
    op.create_index(
        'idx_playlists_user_created',
        'playlists',
        ['user_id', 'created_at'],
        postgresql_using='btree'
    )
    
    # Index for public playlists
    op.create_index(
        'idx_playlists_public',
        'playlists',
        ['is_public'],
        postgresql_using='btree'
    )
    
    # Index for created_at alone (trending playlists)
    op.create_index(
        'idx_playlists_created_at',
        'playlists',
        ['created_at'],
        postgresql_using='btree'
    )
    
    # Playlist songs association table indexes
    # Index for getting songs in a playlist ordered by position
    op.create_index(
        'idx_playlist_songs_order',
        'playlist_songs',
        ['playlist_id', 'position'],
        postgresql_using='btree'
    )
    
    # Index for finding playlists containing a song
    op.create_index(
        'idx_playlist_songs_song',
        'playlist_songs',
        ['song_id'],
        postgresql_using='btree'
    )
    
    # Index for recently added songs to playlists
    op.create_index(
        'idx_playlist_songs_added',
        'playlist_songs',
        ['added_at'],
        postgresql_using='btree'
    )
    
    # Liked songs table indexes
    # Index for user's liked songs
    op.create_index(
        'idx_liked_songs_user',
        'liked_songs',
        ['user_id', 'liked_at'],
        postgresql_using='btree'
    )
    
    # Index for song popularity (how many users liked a song)
    op.create_index(
        'idx_liked_songs_song',
        'liked_songs',
        ['song_id'],
        postgresql_using='btree'
    )
    
    # Genres table indexes
    # Note: name already has unique index from model definition
    # Adding index for parent_genre_id for hierarchical queries
    op.create_index(
        'idx_genres_parent',
        'genres',
        ['parent_genre_id'],
        postgresql_using='btree'
    )
    
    # Song genres association table indexes
    op.create_index(
        'idx_song_genres_song',
        'song_genres',
        ['song_id'],
        postgresql_using='btree'
    )
    
    op.create_index(
        'idx_song_genres_genre',
        'song_genres',
        ['genre_id'],
        postgresql_using='btree'
    )


def downgrade():
    """Remove performance indexes"""
    
    # Drop all indexes in reverse order
    op.drop_index('idx_song_genres_genre', table_name='song_genres')
    op.drop_index('idx_song_genres_song', table_name='song_genres')
    op.drop_index('idx_genres_parent', table_name='genres')
    op.drop_index('idx_liked_songs_song', table_name='liked_songs')
    op.drop_index('idx_liked_songs_user', table_name='liked_songs')
    op.drop_index('idx_playlist_songs_added', table_name='playlist_songs')
    op.drop_index('idx_playlist_songs_song', table_name='playlist_songs')
    op.drop_index('idx_playlist_songs_order', table_name='playlist_songs')
    op.drop_index('idx_playlists_created_at', table_name='playlists')
    op.drop_index('idx_playlists_public', table_name='playlists')
    op.drop_index('idx_playlists_user_created', table_name='playlists')
    op.drop_index('idx_songs_created_at', table_name='songs')
    op.drop_index('idx_songs_release_date', table_name='songs')
    op.drop_index('idx_songs_album', table_name='songs')
    op.drop_index('idx_songs_trending', table_name='songs')
