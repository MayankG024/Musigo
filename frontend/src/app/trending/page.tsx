'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Music, TrendingUp, Award, BarChart3, Clock } from 'lucide-react'
import { Navigation } from '@/components/navigation'
import dynamic from 'next/dynamic'
const MusicPlayer = dynamic(() => import('@/components/music-player').then(m => m.MusicPlayer), { ssr: false })
import { discoveryApi } from '@/lib/api'
import { Song } from '@/types/api'

export default function TrendingPage() {
  const [currentTrack, setCurrentTrack] = useState<Song | null>(null)
  const [selectedPeriod, setSelectedPeriod] = useState<'daily' | 'weekly' | 'monthly'>('daily')

  // Backend has no time-windowed trending yet; map period to result window honestly.
  const periodLimit = selectedPeriod === 'daily' ? 20 : selectedPeriod === 'weekly' ? 35 : 50
  // Fetch trending songs
  const { data: trendingSongs, isLoading } = useQuery({
    queryKey: ['trending-songs', selectedPeriod],
    queryFn: () => discoveryApi.getTrendingSongs(periodLimit),
  })

  // Mock data for charts (you can replace with real API calls)
  const topGenres = [
  { name: 'Pop', count: 45, color: 'bg-emerald-500' },
    { name: 'Hip Hop', count: 38, color: 'bg-blue-500' },
    { name: 'Electronic', count: 32, color: 'bg-green-500' },
    { name: 'Rock', count: 28, color: 'bg-red-500' },
    { name: 'R&B', count: 25, color: 'bg-yellow-500' },
  ]

  return (
  <div className="min-h-screen relative z-10">
      {/* Navigation */}
      <Navigation />

      <div className="container mx-auto px-4 py-8">
        {/* Page Title */}
        <div className="mb-8">
          <h2 className="text-4xl font-bold text-white mb-2">Trending Music</h2>
          <p className="text-lg text-white/70">Discover whats popular right now</p>
        </div>

        {/* Period Selector */}
        <div className="flex space-x-2 mb-8">
          <button
            onClick={() => setSelectedPeriod('daily')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              selectedPeriod === 'daily'
                ? 'bg-emerald-600 text-white'
                : 'bg-white/10 text-white/70 hover:bg-white/20'
            }`}
          >
            Today
          </button>
          <button
            onClick={() => setSelectedPeriod('weekly')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              selectedPeriod === 'weekly'
                ? 'bg-emerald-600 text-white'
                : 'bg-white/10 text-white/70 hover:bg-white/20'
            }`}
          >
            This Week
          </button>
          <button
            onClick={() => setSelectedPeriod('monthly')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              selectedPeriod === 'monthly'
                ? 'bg-emerald-600 text-white'
                : 'bg-white/10 text-white/70 hover:bg-white/20'
            }`}
          >
            This Month
          </button>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Trending List */}
          <div className="lg:col-span-2">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
                <TrendingUp className="w-6 h-6 mr-2" />
                Top 50 Trending
              </h3>
              
              {isLoading ? (
                <div className="space-y-3">
                  {[...Array(10)].map((_, i) => (
                    <div key={i} className="flex items-center space-x-4 p-3 bg-white/5 rounded-lg animate-pulse">
                      <div className="w-8 h-8 bg-white/20 rounded" />
                      <div className="w-12 h-12 bg-white/20 rounded" />
                      <div className="flex-1">
                        <div className="h-4 bg-white/20 rounded w-1/3 mb-2" />
                        <div className="h-3 bg-white/20 rounded w-1/4" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-2">
                  {trendingSongs?.slice(0, 20).map((song, index) => (
                    <div
                      key={song.song_id}
                      onClick={() => setCurrentTrack(song)}
                      className="group flex items-center space-x-4 p-3 bg-white/5 hover:bg-white/10 rounded-lg cursor-pointer transition"
                    >
                      <div className="w-8 text-center">
                        <span className={`font-bold ${index < 3 ? 'text-yellow-400 text-lg' : 'text-white/60'}`}>
                          {index + 1}
                        </span>
                      </div>
                      <div className="w-12 h-12 bg-gradient-to-br from-emerald-600 to-blue-600 rounded flex items-center justify-center flex-shrink-0">
                        {song.album_art_url ? (
                          <img
                            src={song.album_art_url}
                            alt={song.title}
                            className="w-full h-full object-cover rounded"
                          />
                        ) : (
                          <Music className="w-6 h-6 text-white" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-white group-hover:text-emerald-400 truncate">{song.title}</p>
                        <p className="text-sm text-white/60 truncate">{song.artist}</p>
                      </div>
                      <div className="text-right">
                        {song.genre && (
                          <span className="text-xs text-emerald-400">{song.genre}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Side Stats */}
          <div className="space-y-6">
            {/* Top Genres */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Top Genres
              </h3>
              <div className="space-y-3">
                {topGenres.map((genre, index) => (
                  <div key={genre.name}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm text-white/80">{genre.name}</span>
                      <span className="text-xs text-white/60">{genre.count}%</span>
                    </div>
                    <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${genre.color} transition-all duration-500`}
                        style={{ width: `${genre.count}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Rising Stars */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center">
                <Award className="w-5 h-5 mr-2" />
                Rising Stars
              </h3>
              <div className="space-y-3">
                {trendingSongs?.slice(20, 25).map((song) => (
                  <div
                    key={song.song_id}
                    onClick={() => setCurrentTrack(song)}
                    className="group flex items-center space-x-3 p-2 hover:bg-white/10 rounded-lg cursor-pointer transition"
                  >
                    <div className="w-10 h-10 bg-gradient-to-br from-yellow-500 to-orange-500 rounded flex items-center justify-center">
                      <Music className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white group-hover:text-emerald-400 truncate">{song.title}</p>
                      <p className="text-xs text-white/60 truncate">{song.artist}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Stats Card */}
            <div className="bg-gradient-to-br from-emerald-600 to-blue-600 rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center">
                <Clock className="w-5 h-5 mr-2" />
                Platform Stats
              </h3>
              <div className="space-y-3">
                <div>
                  <p className="text-white/80 text-sm">Total Plays Today</p>
                  <p className="text-2xl font-bold text-white">1.2M</p>
                </div>
                <div>
                  <p className="text-white/80 text-sm">Active Users</p>
                  <p className="text-2xl font-bold text-white">45.3K</p>
                </div>
                <div>
                  <p className="text-white/80 text-sm">Songs Discovered</p>
                  <p className="text-2xl font-bold text-white">892K</p>
                </div>
              </div>
            </div>
          </div>
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
