'use client'

import { useState } from 'react'
import { Search, Sparkles, PlayCircle } from 'lucide-react'
import { DiscoverySearch } from '@/components/discovery-search'
import { Navigation } from '@/components/navigation'
import dynamic from 'next/dynamic'
const MusicPlayer = dynamic(() => import('@/components/music-player').then(m => m.MusicPlayer), { ssr: false })
import { RecommendationCard } from '@/components/recommendation-card'
import { SongMarquee } from '@/components/song-marquee'
import { DiscoveryResult } from '@/types/api'

export default function HomePage() {
  const [currentTrack, setCurrentTrack] = useState<DiscoveryResult | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  return (
  <div className="min-h-screen relative z-10">
      {/* Navigation */}
      <Navigation />

      {/* Center Marquee relocated above search - removed from here */}

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 relative z-10">
        <div className="text-center mb-12">
          <h2 className="text-5xl font-extrabold mb-4 tracking-tight" style={{
            background: 'linear-gradient(120deg, var(--spotify-green), var(--bright-cyan))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>Find the music you love</h2>
          <p className="text-xl max-w-2xl mx-auto leading-relaxed" style={{ color: 'var(--text-medium)' }}>
            Use natural language to find your perfect soundtrack. 
            Our AI understands mood, genre, tempo, and more.
          </p>
        </div>

        {/* Marquee above search */}
        <div className="max-w-3xl mx-auto mb-10">
          <SongMarquee onSongClick={(title) => setSearchQuery(title)} />
        </div>
        {/* Discovery Search */}
        <div className="max-w-3xl mx-auto mb-16">
          <DiscoverySearch onSelectTrack={setCurrentTrack} query={searchQuery} onQueryChange={setSearchQuery} />
        </div>

        {/* Section divider (above features) */}
        <div className="my-12">
          <div className="h-px w-full" style={{ background: 'linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,0.06), rgba(255,255,255,0))' }} />
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <div className="flex flex-col">
            <div className="flex items-center gap-4 mb-2">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ background: 'var(--bright-green)' }}>
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold" style={{ color: 'var(--bright-green)' }}>Smart Discovery</h3>
            </div>
            <p className="text-base leading-relaxed" style={{ color: 'var(--text-medium)' }}>
              Describe what you want to hear in plain English.
              Upbeat songs for a morning run or Chill jazz for studying
            </p>
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-4 mb-2">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ background: 'var(--bright-yellow)' }}>
                <Search className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold" style={{ color: 'var(--bright-yellow)' }}>Semantic Search</h3>
            </div>
            <p className="text-base leading-relaxed" style={{ color: 'var(--text-medium)' }}>
              Our AI understands context and meaning, not just keywords.
              Find music that truly matches your vibe.
            </p>
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-4 mb-2">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ background: 'var(--spotify-green)' }}>
                <PlayCircle className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold" style={{ color: 'var(--spotify-green)' }}>Instant Preview</h3>
            </div>
            <p className="text-base leading-relaxed" style={{ color: 'var(--text-medium)' }}>
              Preview tracks instantly before adding to your library.
              Build perfect playlists with confidence.
            </p>
          </div>
        </div>

        {/* Section divider (below features) */}
        <div className="my-12">
          <div className="h-px w-full" style={{ background: 'linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,0.06), rgba(255,255,255,0))' }} />
        </div>

        {/* Recommendations Section */}
        <div className="mb-16">
          <h3 className="text-2xl font-bold text-gray-800 mb-6">Recommended For You</h3>
          <div className="grid md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <RecommendationCard
                key={i}
                title={`Discover Weekly ${i}`}
                description="Your personalized mix"
                imageUrl={`https://picsum.photos/200?random=${i}`}
                onClick={() => {}}
              />
            ))}
          </div>
        </div>
      </section>

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
