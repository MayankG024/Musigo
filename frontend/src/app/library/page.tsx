'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Music, Heart, Clock, ListMusic, Plus, Trash2 } from 'lucide-react'
import { Navigation } from '@/components/navigation'
import dynamic from 'next/dynamic'
const MusicPlayer = dynamic(() => import('@/components/music-player').then(m => m.MusicPlayer), { ssr: false })
import { playlistApi, userApi } from '@/lib/api'
import { Song } from '@/types/api'
import toast from 'react-hot-toast'

export default function LibraryPage() {
  const [currentTrack, setCurrentTrack] = useState<Song | null>(null)
  const [selectedTab, setSelectedTab] = useState<'playlists' | 'favorites' | 'recent'>('playlists')
  const [showCreatePlaylist, setShowCreatePlaylist] = useState(false)
  const [newPlaylistName, setNewPlaylistName] = useState('')
  const queryClient = useQueryClient()

  // Fetch user playlists
  const { data: playlistsData, isLoading: loadingPlaylists } = useQuery({
    queryKey: ['my-playlists'],
    queryFn: () => playlistApi.getMyPlaylists(1, 20),
  })

  // Fetch favorites
  const { data: favoritesData, isLoading: loadingFavorites } = useQuery({
    queryKey: ['favorites'],
    queryFn: () => userApi.getFavorites(1, 50),
    enabled: selectedTab === 'favorites',
  })

  // Fetch recently played
  const { data: recentSongs, isLoading: loadingRecent } = useQuery({
    queryKey: ['recently-played'],
    queryFn: () => userApi.getRecentlyPlayed(20),
    enabled: selectedTab === 'recent',
  })

  // Create playlist mutation
  const createPlaylistMutation = useMutation({
    mutationFn: (name: string) => playlistApi.createPlaylist({ name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-playlists'] })
      setShowCreatePlaylist(false)
      setNewPlaylistName('')
      toast.success('Playlist created successfully!')
    },
    onError: () => {
      toast.error('Failed to create playlist')
    },
  })

  // Remove favorite mutation
  const removeFavoriteMutation = useMutation({
    mutationFn: (songId: string) => userApi.removeFavorite(songId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorites'] })
      toast.success('Removed from favorites')
    },
    onError: () => {
      toast.error('Failed to remove from favorites')
    },
  })

  const handleCreatePlaylist = (e: React.FormEvent) => {
    e.preventDefault()
    if (newPlaylistName.trim()) {
      createPlaylistMutation.mutate(newPlaylistName)
    }
  }

  return (
  <div className="min-h-screen relative z-10">
      {/* Navigation */}
      <Navigation />

      <div className="container mx-auto px-4 py-8">
        {/* Page Title */}
        <div className="mb-8">
          <h2 className="text-4xl font-bold text-white mb-2">My Library</h2>
          <p className="text-lg text-white/70">Your playlists, favorites, and listening history</p>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 mb-8 bg-white/10 backdrop-blur-lg rounded-lg p-1 inline-flex">
          <button
            onClick={() => setSelectedTab('playlists')}
            className={`px-6 py-2 rounded-md font-medium transition ${
              selectedTab === 'playlists'
                ? 'bg-emerald-600 text-white'
                : 'text-white/70 hover:text-white'
            }`}
          >
            <ListMusic className="w-4 h-4 inline mr-2" />
            Playlists
          </button>
          <button
            onClick={() => setSelectedTab('favorites')}
            className={`px-6 py-2 rounded-md font-medium transition ${
              selectedTab === 'favorites'
                ? 'bg-emerald-600 text-white'
                : 'text-white/70 hover:text-white'
            }`}
          >
            <Heart className="w-4 h-4 inline mr-2" />
            Favorites
          </button>
          <button
            onClick={() => setSelectedTab('recent')}
            className={`px-6 py-2 rounded-md font-medium transition ${
              selectedTab === 'recent'
                ? 'bg-emerald-600 text-white'
                : 'text-white/70 hover:text-white'
            }`}
          >
            <Clock className="w-4 h-4 inline mr-2" />
            Recently Played
          </button>
        </div>

        {/* Content */}
        <div className="min-h-[400px]">
          {/* Playlists Tab */}
          {selectedTab === 'playlists' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-2xl font-bold text-white">Your Playlists</h3>
                <button
                  onClick={() => setShowCreatePlaylist(true)}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium transition flex items-center"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create Playlist
                </button>
              </div>

              {/* Create Playlist Modal */}
              {showCreatePlaylist && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                  <div className="bg-gray-900 rounded-lg p-6 w-96">
                    <h3 className="text-xl font-bold text-white mb-4">Create New Playlist</h3>
                    <form onSubmit={handleCreatePlaylist}>
                      <input
                        type="text"
                        value={newPlaylistName}
                        onChange={(e) => setNewPlaylistName(e.target.value)}
                        placeholder="Playlist name"
                        className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-emerald-500 mb-4"
                        autoFocus
                      />
                      <div className="flex justify-end space-x-3">
                        <button
                          type="button"
                          onClick={() => setShowCreatePlaylist(false)}
                          className="px-4 py-2 text-white/70 hover:text-white transition"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          disabled={!newPlaylistName.trim() || createPlaylistMutation.isPending}
                          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium transition disabled:opacity-50"
                        >
                          Create
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              )}

              {loadingPlaylists ? (
                <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {[...Array(4)].map((_, i) => (
                    <div key={i} className="bg-white/10 backdrop-blur-lg rounded-lg p-4 animate-pulse">
                      <div className="aspect-square bg-white/20 rounded-lg mb-3" />
                      <div className="h-4 bg-white/20 rounded mb-2" />
                      <div className="h-3 bg-white/20 rounded w-2/3" />
                    </div>
                  ))}
                </div>
              ) : playlistsData?.items && playlistsData.items.length > 0 ? (
                <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {playlistsData.items.map((playlist) => (
                    <a
                      key={playlist.id}
                      href={`/playlist/${playlist.id}`}
                      className="group cursor-pointer bg-white/10 backdrop-blur-lg rounded-lg p-4 hover:bg-white/20 transition border border-white/10"
                    >
                      <div className="aspect-square rounded-lg overflow-hidden mb-3 bg-gradient-to-br from-emerald-600 to-blue-600 flex items-center justify-center">
                        <ListMusic className="w-16 h-16 text-white/50" />
                      </div>
                      <h4 className="font-semibold text-white group-hover:text-emerald-400 text-sm mb-1 truncate">
                        {playlist.name}
                      </h4>
                      <p className="text-xs text-white/60">
                        {playlist.song_count || 0} songs
                      </p>
                    </a>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <ListMusic className="w-16 h-16 text-white/30 mx-auto mb-4" />
                  <p className="text-white/60 mb-4">No playlists yet</p>
                  <button
                    onClick={() => setShowCreatePlaylist(true)}
                    className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-full font-medium transition"
                  >
                    Create Your First Playlist
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Favorites Tab */}
          {selectedTab === 'favorites' && (
            <div>
              <h3 className="text-2xl font-bold text-white mb-6">Favorite Songs</h3>
              {loadingFavorites ? (
                <div className="space-y-3">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="bg-white/10 backdrop-blur-lg rounded-lg p-4 animate-pulse">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-white/20 rounded" />
                        <div className="flex-1">
                          <div className="h-4 bg-white/20 rounded w-1/3 mb-2" />
                          <div className="h-3 bg-white/20 rounded w-1/4" />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : favoritesData?.items && favoritesData.items.length > 0 ? (
                <div className="space-y-3">
                  {favoritesData.items.map((favorite) => (
                    <div
                      key={favorite.id}
                      className="group flex items-center justify-between p-4 bg-white/10 backdrop-blur-lg rounded-lg hover:bg-white/20 transition"
                    >
                      <div
                        className="flex items-center space-x-4 flex-1 cursor-pointer"
                        onClick={() => setCurrentTrack(favorite.song)}
                      >
                        <div className="w-12 h-12 bg-gradient-to-br from-emerald-600 to-blue-600 rounded flex items-center justify-center">
                          <Music className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <p className="font-medium text-white group-hover:text-emerald-400">{favorite.song.title}</p>
                          <p className="text-sm text-white/60">{favorite.song.artist}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => removeFavoriteMutation.mutate(favorite.song_id)}
                        className="p-2 text-white/60 hover:text-red-400 transition"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Heart className="w-16 h-16 text-white/30 mx-auto mb-4" />
                  <p className="text-white/60 mb-4">No favorite songs yet</p>
                  <a
                    href="/discover"
                    className="inline-block px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-full font-medium transition"
                  >
                    Discover Music
                  </a>
                </div>
              )}
            </div>
          )}

          {/* Recently Played Tab */}
          {selectedTab === 'recent' && (
            <div>
              <h3 className="text-2xl font-bold text-white mb-6">Recently Played</h3>
              {loadingRecent ? (
                <div className="space-y-3">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="bg-white/10 backdrop-blur-lg rounded-lg p-4 animate-pulse">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-white/20 rounded" />
                        <div className="flex-1">
                          <div className="h-4 bg-white/20 rounded w-1/3 mb-2" />
                          <div className="h-3 bg-white/20 rounded w-1/4" />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : recentSongs && recentSongs.length > 0 ? (
                <div className="space-y-3">
                  {recentSongs.map((song) => (
                    <div
                      key={song.song_id}
                      onClick={() => setCurrentTrack(song)}
                      className="group flex items-center space-x-4 p-4 bg-white/10 backdrop-blur-lg rounded-lg hover:bg-white/20 transition cursor-pointer"
                    >
                      <div className="w-12 h-12 bg-gradient-to-br from-emerald-600 to-blue-600 rounded flex items-center justify-center">
                        <Music className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-white group-hover:text-emerald-400">{song.title}</p>
                        <p className="text-sm text-white/60">{song.artist}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Clock className="w-16 h-16 text-white/30 mx-auto mb-4" />
                  <p className="text-white/60 mb-4">No recently played songs</p>
                  <a
                    href="/discover"
                    className="inline-block px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-full font-medium transition"
                  >
                    Start Listening
                  </a>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Music Player */}
      {currentTrack && (
        <MusicPlayer
          track={currentTrack}
          onClose={() => setCurrentTrack(null)}
        />
      )}
    </div>
  )
}
