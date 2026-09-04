'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { TrendingUp, Sparkles, Radio } from 'lucide-react'
import { DiscoverySearch } from '@/components/discovery-search'
import { Navigation } from '@/components/navigation'
import dynamic from 'next/dynamic'
const MusicPlayer = dynamic(() => import('@/components/music-player').then(m => m.MusicPlayer), { ssr: false })
import { discoveryApi } from '@/lib/api'
import { Song, DiscoveryResult } from '@/types/api'

export default function DiscoverPage() {
  const [currentTrack, setCurrentTrack] = useState<Song | null>(null)
  const [selectedGenre, setSelectedGenre] = useState<string>('')
  const [recommendations, setRecommendations] = useState<Song[]>([])
  const [loadingRecs, setLoadingRecs] = useState(false)

  // Fetch trending songs
  const { data: trendingSongs, isLoading: loadingTrending } = useQuery({
    queryKey: ['trending-songs'],
    queryFn: () => discoveryApi.getTrendingSongs(12),
  })

  // Fetch available genres
  const { data: genres } = useQuery({
    queryKey: ['genres'],
    queryFn: () => discoveryApi.getGenres(),
  })

  const handleSelectTrack = (track: DiscoveryResult | Song) => {
    setCurrentTrack(track)
  }

  const filteredTrending = (trendingSongs ?? []).filter((s) =>
    selectedGenre ? (s.genre ?? '') === selectedGenre : true
  )

  const handleGenerateRecommendations = async () => {
    const seeds = (trendingSongs ?? []).slice(0, 3).map((s) => String(s.song_id))
    if (seeds.length === 0) return
    setLoadingRecs(true)
    try {
      const recs = await discoveryApi.getRecommendations({ seed_songs: seeds, limit: 8 })
      setRecommendations(recs as unknown as Song[])
    } finally {
      setLoadingRecs(false)
    }
  }

  return (
    <div className="min-h-screen relative z-10">
      {/* Navigation */}
      <Navigation />

      <div className="container mx-auto px-4 py-8">
        {/* Page Title */}
        <div className="mb-8">
          <h2 className="text-4xl font-bold text-musigo-green-800 mb-2">Discover New Music</h2>
          <p className="text-lg text-musigo-green-700">Use AI to find your next favorite songs</p>
        </div>

        {/* Discovery Search */}
        <div className="mb-12">
          <DiscoverySearch onSelectTrack={handleSelectTrack} />
        </div>

        {/* Genre Filter */}
        {genres && genres.length > 0 && (
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-musigo-green-800 mb-4 flex items-center">
              <Radio className="w-5 h-5 mr-2" />
              Browse by Genre
            </h3>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedGenre('')}
                className={`px-4 py-2 rounded-full transition ${
                  selectedGenre === ''
                    ? 'bg-musigo-green-600 text-musigo-beige-50'
                    : 'bg-musigo-beige-100/60 text-musigo-green-700 hover:bg-musigo-beige-100/80'
                }`}
              >
                All Genres
              </button>
              {genres.slice(0, 10).map((genre) => (
                <button
                  key={genre}
                  onClick={() => setSelectedGenre(genre)}
                  className={`px-4 py-2 rounded-full transition ${
                    selectedGenre === genre
                      ? 'bg-musigo-green-600 text-musigo-beige-50'
                      : 'bg-musigo-beige-100/60 text-musigo-green-700 hover:bg-musigo-beige-100/80'
                  }`}
                >
                  {genre}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Trending Songs */}
        <div className="mb-12">
          <h3 className="text-2xl font-bold text-musigo-green-800 mb-6 flex items-center">
            <TrendingUp className="w-6 h-6 mr-2" />
            Trending Now
          </h3>
          {loadingTrending ? (
            <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-4">
              {[...Array(8)].map((_, i) => (
                <div
                  key={i}
                  className="bg-white/10 backdrop-blur-lg rounded-lg p-4 animate-pulse"
                >
                  <div className="aspect-square bg-white/20 rounded-lg mb-3" />
                  <div className="h-4 bg-white/20 rounded mb-2" />
                  <div className="h-3 bg-white/20 rounded w-2/3" />
                </div>
              ))}
            </div>
          ) : (
            <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-4">
              {filteredTrending.map((song) => (
                <div
                  key={song.song_id}
                  onClick={() => handleSelectTrack(song)}
                  className="group cursor-pointer bg-white/10 backdrop-blur-lg rounded-lg p-4 hover:bg-white/20 transition border border-white/10"
                >
                  <div className="aspect-square rounded-lg overflow-hidden mb-3 bg-gradient-to-br from-emerald-600 to-blue-600">
                    {song.album_art_url && (
                      <img
                        src={song.album_art_url}
                        alt={song.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    )}
                  </div>
                  <h4 className="font-semibold text-white text-sm mb-1 truncate">
                    {song.title}
                  </h4>
                  <p className="text-xs text-white/60 truncate">{song.artist}</p>
                  {song.genre && (
                    <span className="inline-block mt-2 px-2 py-1 text-xs bg-emerald-600/30 text-emerald-300 rounded-full">
                      {song.genre}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* AI Recommendations Section */}
        <div className="mb-12">
          <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
            <Sparkles className="w-6 h-6 mr-2" />
            AI Recommendations
          </h3>
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <p className="text-white/80 mb-4">
              Get personalized recommendations based on your listening history and preferences.
            </p>
            <button
              onClick={handleGenerateRecommendations}
              disabled={loadingRecs}
              className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-full font-medium transition disabled:opacity-50"
            >
              {loadingRecs ? 'Generating…' : 'Generate Recommendations'}
            </button>
            {recommendations.length > 0 && (
              <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-4 mt-6">
                {recommendations.map((song) => (
                  <div
                    key={song.song_id}
                    onClick={() => handleSelectTrack(song)}
                    className="group cursor-pointer bg-white/10 backdrop-blur-lg rounded-lg p-4 hover:bg-white/20 transition border border-white/10"
                  >
                    <h4 className="font-semibold text-white text-sm mb-1 truncate">{song.title}</h4>
                    <p className="text-xs text-white/60 truncate">{song.artist}</p>
                  </div>
                ))}
              </div>
            )}
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
