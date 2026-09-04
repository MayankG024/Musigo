'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Music, Play, Trash2, Plus, Edit2, Lock, Globe } from 'lucide-react'
import { MusicPlayer } from '@/components/music-player'
import { Navigation } from '@/components/navigation'
import { playlistApi, discoveryApi } from '@/lib/api'
import { Song } from '@/types/api'
import toast from 'react-hot-toast'

export default function PlaylistDetailPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const playlistId = params.id as string

  const [currentTrack, setCurrentTrack] = useState<Song | null>(null)
  const [playQueue, setPlayQueue] = useState<Song[]>([])
  const [isEditing, setIsEditing] = useState(false)
  const [editData, setEditData] = useState({ name: '', description: '' })
  const [showAddSongs, setShowAddSongs] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [addedSongIds, setAddedSongIds] = useState<Set<string>>(new Set())

  // Fetch playlist details
  const { data: playlist, isLoading } = useQuery({
    queryKey: ['playlist', playlistId],
    queryFn: () => playlistApi.getPlaylistById(playlistId),
  })

  // Fetch playlist songs
  const { data: songs } = useQuery({
    queryKey: ['playlist-songs', playlistId],
    queryFn: () => playlistApi.getPlaylistSongs(playlistId),
    enabled: !!playlist,
  })

  // Search for songs to add
  const { data: searchResults } = useQuery({
    queryKey: ['song-search', searchQuery],
    queryFn: () => discoveryApi.searchSongs(searchQuery, 10),
    enabled: searchQuery.length > 2,
  })

  // Update playlist mutation
  const updatePlaylistMutation = useMutation({
    mutationFn: (data: { name?: string; description?: string }) =>
      playlistApi.updatePlaylist(playlistId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playlist', playlistId] })
      setIsEditing(false)
      toast.success('Playlist updated successfully')
    },
    onError: () => {
      toast.error('Failed to update playlist')
    },
  })

  // Delete playlist mutation
  const deletePlaylistMutation = useMutation({
    mutationFn: () => playlistApi.deletePlaylist(playlistId),
    onSuccess: () => {
      toast.success('Playlist deleted successfully')
      router.push('/library')
    },
    onError: () => {
      toast.error('Failed to delete playlist')
    },
  })

  // Add song to playlist mutation
  const addSongMutation = useMutation({
    mutationFn: (songId: string) => playlistApi.addSongToPlaylist(playlistId, songId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playlist-songs', playlistId] })
      toast.success('Song added to playlist')
    },
    onError: () => {
      toast.error('Failed to add song')
    },
  })

  // Remove song from playlist mutation
  const removeSongMutation = useMutation({
    mutationFn: (songId: string) => playlistApi.removeSongFromPlaylist(playlistId, songId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playlist-songs', playlistId] })
      toast.success('Song removed from playlist')
    },
    onError: () => {
      toast.error('Failed to remove song')
    },
  })

  useEffect(() => {
    if (playlist) {
      setEditData({
        name: playlist.name,
        description: playlist.description || '',
      })
    }
  }, [playlist])

  useEffect(() => {
    if (!showAddSongs) {
      setAddedSongIds(new Set())
      setSearchQuery('')
    }
  }, [showAddSongs])

  const handleSaveEdit = () => {
    updatePlaylistMutation.mutate(editData)
  }

  const handlePlayAll = () => {
    if (songs && songs.length > 0) {
      setCurrentTrack(songs[0])
      setPlayQueue(songs)
      toast.success(`Playing ${songs.length} songs`)
    }
  }

  const handleDeletePlaylist = () => {
    if (confirm('Are you sure you want to delete this playlist?')) {
      deletePlaylistMutation.mutate()
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-900 via-blue-900 to-indigo-900">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-white/20 rounded w-1/3 mb-4" />
            <div className="h-4 bg-white/20 rounded w-1/2 mb-8" />
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-16 bg-white/10 rounded-lg" />
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!playlist) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-900 via-blue-900 to-indigo-900">
        <Navigation />
        <div className="container mx-auto px-4 py-8 text-center">
          <p className="text-white/60">Playlist not found</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-900 via-blue-900 to-indigo-900">
      <Navigation />

      <div className="container mx-auto px-4 py-8">
        {/* Playlist Header */}
        <div className="mb-8">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {isEditing ? (
                <div className="space-y-4">
                  <input
                    type="text"
                    value={editData.name}
                    onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                    className="text-4xl font-bold bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
                  />
                  <textarea
                    value={editData.description}
                    onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                    placeholder="Add a description..."
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white placeholder-white/50"
                    rows={2}
                  />
                  <div className="flex space-x-3">
                    <button
                      onClick={handleSaveEdit}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium transition"
                    >
                      Save
                    </button>
                    <button
                      onClick={() => setIsEditing(false)}
                      className="px-4 py-2 text-white/70 hover:text-white transition"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <h1 className="text-4xl font-bold text-white mb-2">{playlist.name}</h1>
                  {playlist.description && (
                    <p className="text-lg text-white/70 mb-2">{playlist.description}</p>
                  )}
                  <div className="flex items-center space-x-4 text-white/60">
                    <span className="flex items-center">
                      {playlist.is_public ? (
                        <>
                          <Globe className="w-4 h-4 mr-1" /> Public
                        </>
                      ) : (
                        <>
                          <Lock className="w-4 h-4 mr-1" /> Private
                        </>
                      )}
                    </span>
                    <span>{songs?.length || 0} songs</span>
                  </div>
                </>
              )}
            </div>

            {/* Action Buttons */}
            {!isEditing && (
              <div className="flex items-center space-x-3">
                <button
                  onClick={handlePlayAll}
                  disabled={!songs || songs.length === 0}
                  className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-full font-medium transition flex items-center disabled:opacity-50"
                >
                  <Play className="w-5 h-5 mr-2" />
                  Play All
                </button>
                <button
                  onClick={() => setShowAddSongs(true)}
                  className="p-3 bg-white/10 hover:bg-white/20 rounded-full transition"
                >
                  <Plus className="w-5 h-5 text-white" />
                </button>
                <button
                  onClick={() => setIsEditing(true)}
                  className="p-3 bg-white/10 hover:bg-white/20 rounded-full transition"
                >
                  <Edit2 className="w-5 h-5 text-white" />
                </button>
                <button
                  onClick={handleDeletePlaylist}
                  className="p-3 bg-white/10 hover:bg-red-600/20 rounded-full transition group"
                >
                  <Trash2 className="w-5 h-5 text-white group-hover:text-red-400" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Songs List */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          {songs && songs.length > 0 ? (
            <div className="space-y-2">
              {songs.map((song, index) => (
                <div
                  key={song.song_id}
                  className="flex items-center justify-between p-3 bg-white/5 hover:bg-white/10 rounded-lg transition"
                >
                  <div className="flex items-center space-x-4 flex-1">
                    <span className="text-white/60 w-8 text-center">{index + 1}</span>
                    <div
                      className="flex items-center space-x-4 flex-1 cursor-pointer"
                      onClick={() => {
                        setCurrentTrack(song)
                        setPlayQueue(songs.slice(index))
                      }}
                    >
                      <div className="w-12 h-12 bg-gradient-to-br from-emerald-600 to-blue-600 rounded flex items-center justify-center">
                        <Music className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-white">{song.title}</p>
                        <p className="text-sm text-white/60">{song.artist}</p>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => removeSongMutation.mutate(song.song_id)}
                    className="p-2 text-white/60 hover:text-red-400 transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Music className="w-16 h-16 text-white/30 mx-auto mb-4" />
              <p className="text-white/60 mb-4">No songs in this playlist yet</p>
              <button
                onClick={() => setShowAddSongs(true)}
                className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-full font-medium transition"
              >
                Add Songs
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Add Songs Modal */}
      {showAddSongs && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
            <h3 className="text-xl font-bold text-white mb-4">Add Songs to Playlist</h3>
            
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for songs..."
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-emerald-500 mb-4"
            />

            <div className="flex-1 overflow-y-auto">
              {searchResults && searchResults.length > 0 ? (
                <div className="space-y-2">
                  {searchResults.filter(song => !addedSongIds.has(song.song_id)).map((song) => (
                    <div
                      key={song.song_id}
                      className="flex items-center justify-between p-3 bg-white/5 hover:bg-white/10 rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-emerald-600 to-blue-600 rounded flex items-center justify-center">
                          <Music className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <p className="font-medium text-white">{song.title}</p>
                          <p className="text-sm text-white/60">{song.artist}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => {
                          addSongMutation.mutate(song.song_id)
                          setAddedSongIds(prev => {
                            const newSet = new Set(prev)
                            newSet.add(song.song_id)
                            return newSet
                          })
                        }}
                        className="px-4 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium transition"
                      >
                        Add
                      </button>
                    </div>
                  ))}
                </div>
              ) : searchQuery.length > 2 ? (
                <p className="text-white/60 text-center py-8">No songs found</p>
              ) : (
                <p className="text-white/60 text-center py-8">Start typing to search for songs</p>
              )}
            </div>

            <div className="mt-4 flex justify-end">
              <button
                onClick={() => setShowAddSongs(false)}
                className="px-4 py-2 text-white/70 hover:text-white transition"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Music Player */}
      {currentTrack && (
        <MusicPlayer
          track={currentTrack}
          queue={playQueue}
          onClose={() => setCurrentTrack(null)}
        />
      )}
    </div>
  )
}
