'use client'

import { Play, Pause, SkipForward, SkipBack, X, Volume2, Volume1, VolumeX, ListMusic, Heart } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import { Song } from '@/types/api'
import { userApi } from '@/lib/api'
import toast from 'react-hot-toast'

interface MusicPlayerProps {
  track: Song
  onClose: () => void
  queue?: Song[]
  onTrackChange?: (track: Song, index: number) => void
}

export function MusicPlayer({ track, onClose, queue = [], onTrackChange }: MusicPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(0.7)
  const [showVolume, setShowVolume] = useState(false)
  const [showQueue, setShowQueue] = useState(false)
  const [isFavorite, setIsFavorite] = useState(false)
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0)
  const audioRef = useRef<HTMLAudioElement>(null)
  const [playQueue, setPlayQueue] = useState<Song[]>(queue)

  // Keep queue in sync when parent passes a new queue; keep index valid.
  useEffect(() => {
    setPlayQueue(queue)
    setCurrentTrackIndex((prev) => Math.min(prev, Math.max(queue.length - 1, 0)))
  }, [queue])

  // Effective track: queue item wins when a queue is provided, else the single track prop.
  const displayTrack = playQueue.length > 0 ? playQueue[currentTrackIndex] ?? track : track

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => setCurrentTime(audio.currentTime)
    const updateDuration = () => setDuration(audio.duration)
    const handleEnded = () => {
      if (currentTrackIndex < playQueue.length - 1) {
        const nextIndex = currentTrackIndex + 1
        setCurrentTrackIndex(nextIndex)
        const next = playQueue[nextIndex]
        if (next) onTrackChange?.(next, nextIndex)
      } else {
        setIsPlaying(false)
      }
    }

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('loadedmetadata', updateDuration)
    audio.addEventListener('ended', handleEnded)
    audio.volume = volume

    // Add to recently played
    if (displayTrack.song_id) {
      userApi.addToRecentlyPlayed(displayTrack.song_id).catch(() => {})
    }

    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('loadedmetadata', updateDuration)
      audio.removeEventListener('ended', handleEnded)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [displayTrack, volume, currentTrackIndex, playQueue])

  // Check if track is favorite
  useEffect(() => {
    if (displayTrack.song_id) {
      userApi.isFavorite(displayTrack.song_id).then(setIsFavorite).catch(() => {})
    }
  }, [displayTrack])

  const togglePlay = () => {
    if (!audioRef.current) return
    
    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  const handleNext = () => {
    if (currentTrackIndex < playQueue.length - 1) {
      const nextIndex = currentTrackIndex + 1
      setCurrentTrackIndex(nextIndex)
      const next = playQueue[nextIndex]
      if (next) {
        onTrackChange?.(next, nextIndex)
        toast(`Playing next: ${next.title}`, { icon: '🎵' })
      }
    }
  }

  const handlePrevious = () => {
    if (currentTrackIndex > 0) {
      const prevIndex = currentTrackIndex - 1
      setCurrentTrackIndex(prevIndex)
      const prev = playQueue[prevIndex]
      if (prev) {
        onTrackChange?.(prev, prevIndex)
        toast(`Playing previous: ${prev.title}`, { icon: '🎵' })
      }
    }
  }

  const handleVolumeChange = (newVolume: number) => {
    setVolume(newVolume)
    if (audioRef.current) {
      audioRef.current.volume = newVolume
    }
  }

  const toggleFavorite = async () => {
    if (!displayTrack.song_id) return

    try {
      if (isFavorite) {
        await userApi.removeFavorite(displayTrack.song_id)
        toast.success('Removed from favorites')
      } else {
        await userApi.addFavorite(displayTrack.song_id)
        toast.success('Added to favorites')
      }
      setIsFavorite(!isFavorite)
    } catch (error) {
      // Public mode: if backend rejects, surface a generic message
      toast.error('Could not update favorites')
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  const getVolumeIcon = () => {
    if (volume === 0) return <VolumeX className="w-5 h-5" />
    if (volume < 0.5) return <Volume1 className="w-5 h-5" />
    return <Volume2 className="w-5 h-5" />
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-black/90 backdrop-blur-xl border-t border-white/10 p-4">
      <div className="container mx-auto flex items-center justify-between">
        {/* Track Info */}
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-emerald-600 rounded-lg flex items-center justify-center">
            <Volume2 className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="font-medium text-white">{displayTrack.title}</p>
            <p className="text-sm text-white/60">{displayTrack.artist}</p>
          </div>
        </div>

        {/* Player Controls */}
        <div className="flex items-center space-x-6">
          <button
            onClick={handlePrevious}
            disabled={playQueue.length === 0 || currentTrackIndex === 0}
            className="text-white/60 hover:text-emerald-400 transition disabled:opacity-30"
          >
            <SkipBack className="w-5 h-5" />
          </button>
          <button
            onClick={togglePlay}
            className="w-12 h-12 bg-emerald-600 hover:bg-emerald-700 rounded-full flex items-center justify-center transition"
          >
            {isPlaying ? (
              <Pause className="w-6 h-6 text-white" />
            ) : (
              <Play className="w-6 h-6 text-white ml-0.5" />
            )}
          </button>
          <button 
            onClick={handleNext}
            disabled={currentTrackIndex >= playQueue.length - 1}
            className="text-white/60 hover:text-emerald-400 transition disabled:opacity-30"
          >
            <SkipForward className="w-5 h-5" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="flex items-center space-x-3 flex-1 max-w-md mx-8">
          <span className="text-xs text-white/60">{formatTime(currentTime)}</span>
          <div className="flex-1 h-1 bg-white/20 rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-600 transition-all"
              style={{ width: `${(currentTime / duration) * 100 || 0}%` }}
            />
          </div>
          <span className="text-xs text-white/60">{formatTime(duration)}</span>
        </div>

        {/* Additional Controls */}
        <div className="flex items-center space-x-3">
          {/* Favorite Button */}
          <button
            onClick={toggleFavorite}
            className={`text-white/60 hover:text-white transition ${
              isFavorite ? 'text-red-500' : ''
            }`}
          >
            <Heart className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
          </button>

          {/* Volume Control */}
          <div className="relative">
            <button
              onClick={() => setShowVolume(!showVolume)}
              className="text-white/60 hover:text-emerald-400 transition"
            >
              {getVolumeIcon()}
            </button>
            {showVolume && (
              <div className="absolute bottom-full mb-2 right-0 bg-gray-900 rounded-lg p-3 shadow-xl">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={volume}
                  onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                  className="w-24 h-1 bg-white/20 rounded-full appearance-none cursor-pointer"
                  style={{
                    background: `linear-gradient(to right, rgb(5 150 105) 0%, rgb(5 150 105) ${volume * 100}%, rgba(255, 255, 255, 0.2) ${volume * 100}%, rgba(255, 255, 255, 0.2) 100%)`
                  }}
                />
              </div>
            )}
          </div>

          {/* Queue Button */}
          {playQueue.length > 0 && (
            <button
              onClick={() => setShowQueue(!showQueue)}
              className="text-white/60 hover:text-emerald-400 transition relative"
            >
              <ListMusic className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-600 rounded-full text-xs text-white flex items-center justify-center">
                {playQueue.length}
              </span>
            </button>
          )}

          {/* Close Button */}
          <button
            onClick={onClose}
            className="text-white/60 hover:text-emerald-400 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Queue Panel */}
      {showQueue && playQueue.length > 0 && (
        <div className="absolute bottom-full mb-2 right-4 w-80 max-h-96 bg-gray-900 rounded-lg shadow-xl border border-white/10 overflow-hidden">
          <div className="p-3 border-b border-white/10">
            <h3 className="font-semibold text-white">Queue ({playQueue.length} songs)</h3>
          </div>
          <div className="overflow-y-auto max-h-80">
            {playQueue.map((song, index) => (
              <div
                key={`${song.song_id}-${index}`}
                onClick={() => {
                  setCurrentTrackIndex(index)
                  onTrackChange?.(song, index)
                }}
                className={`px-3 py-2 hover:bg-white/10 transition cursor-pointer ${
                  index === currentTrackIndex ? 'bg-emerald-600/20' : ''
                }`}
              >
                <p className="text-sm text-white truncate">{song.title}</p>
                <p className="text-xs text-white/60 truncate">{song.artist}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hidden Audio Element */}
      {displayTrack.preview_url ? (
        <audio key={displayTrack.song_id ?? displayTrack.preview_url} ref={audioRef} src={displayTrack.preview_url} />
      ) : (
        <p className="sr-only">Preview unavailable for this track</p>
      )}
    </div>
  )
}
