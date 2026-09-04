'use client'

import { useState } from 'react'
import { Search, Loader2, Music2 } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { discoveryApi } from '@/lib/api'
import { DiscoveryResult } from '@/types/api'

interface DiscoverySearchProps {
  onSelectTrack: (track: DiscoveryResult) => void
  query?: string
  onQueryChange?: (value: string) => void
}

export function DiscoverySearch({ onSelectTrack, query: controlledQuery, onQueryChange }: DiscoverySearchProps) {
  const [uncontrolledQuery, setUncontrolledQuery] = useState('')
  const query = controlledQuery !== undefined ? controlledQuery : uncontrolledQuery
  const setQuery = onQueryChange || setUncontrolledQuery
  const [results, setResults] = useState<DiscoveryResult[]>([])

  const discoverMutation = useMutation({
    mutationFn: async (searchQuery: string) => {
      return discoveryApi.discover({ query: searchQuery, limit: 10 })
    },
    onSuccess: (data) => {
      setResults(data)
      if (data.length === 0) {
        toast('No results found. Try a different query!', {
          icon: 'ℹ️',
        })
      }
    },
    onError: () => {
      toast.error('Failed to search. Please try again.')
    },
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      discoverMutation.mutate(query)
    }
  }

  const exampleQueries = [
    "Upbeat songs for a morning workout",
    "Relaxing jazz for studying",
    "Happy indie music for a road trip",
    "Dark electronic music with heavy bass",
  ]

  return (
    <div className="w-full">
      <form onSubmit={handleSearch} className="relative mb-6">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe the music you want to hear..."
          className="w-full px-6 py-4 pr-12 text-lg glass rounded-2xl placeholder-gray-400 focus:outline-none shadow-xl transition-all duration-200"
          style={{
            color: 'var(--text-bright)',
            borderColor: 'var(--glass-border)',
            borderWidth: '2px'
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = 'var(--spotify-green)';
            e.currentTarget.style.boxShadow = '0 0 20px rgba(29, 185, 84, 0.3)';
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = 'var(--glass-border)';
            e.currentTarget.style.boxShadow = '';
          }}
        />
        <button
          type="submit"
          disabled={discoverMutation.isPending}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-3 rounded-xl transition-all duration-200 disabled:opacity-50 shadow-lg transform hover:scale-105"
          style={{
            background: `linear-gradient(135deg, var(--spotify-green), var(--bright-blue), var(--bright-cyan))`,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.boxShadow = '0 0 30px rgba(29, 185, 84, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.boxShadow = '';
          }}
        >
          {discoverMutation.isPending ? (
            <Loader2 className="w-6 h-6 text-white animate-spin" />
          ) : (
            <Search className="w-6 h-6 text-white" />
          )}
        </button>
      </form>

      {/* Example Queries */}
      <div className="mb-8">
        <p className="text-sm mb-3 font-bold" style={{ color: 'var(--text-medium)' }}>Try these colorful examples:</p>
        <div className="flex flex-wrap gap-3">
          {exampleQueries.map((example, index) => {
            const colors = [
              'var(--bright-green)',
              'var(--bright-yellow)',
              'var(--bright-blue)',
              'var(--spotify-green)'
            ];
            const color = colors[index % 4];
            return (
              <button
                key={example}
                onClick={() => setQuery(example)}
                className="example-chip text-sm focus:outline-none"
                style={{
                  // supply CSS variable for gradient & interactions
                  '--chip-color': color,
                  color: color
                } as React.CSSProperties}
              >
                {example}
              </button>
            );
          })}
        </div>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="glass rounded-2xl p-6 border-2 shadow-xl" style={{ borderColor: 'var(--glass-border)' }}>
          <h3 className="text-lg font-bold mb-6" style={{ 
            background: `linear-gradient(135deg, var(--bright-green), var(--bright-yellow), var(--spotify-green))`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Discovery Results
          </h3>
          <div className="space-y-3">
            {results.map((result, index) => {
              const colors = [
                'var(--bright-green)',
                'var(--bright-yellow)',
                'var(--bright-blue)',
                'var(--spotify-green)'
              ];
              return (
                <div
                  key={result.song_id}
                  onClick={() => onSelectTrack(result)}
                  className="flex items-center justify-between p-4 glass rounded-xl cursor-pointer transition-all duration-200 border-2 shadow-lg hover:shadow-xl transform hover:scale-102"
                  style={{ borderColor: 'var(--glass-border)' }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = colors[index % 4];
                    e.currentTarget.style.boxShadow = `0 0 20px ${colors[index % 4]}44`;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'var(--glass-border)';
                    e.currentTarget.style.boxShadow = '';
                  }}
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center shadow-lg" style={{
                      background: colors[index % 4]
                    }}>
                      <Music2 className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <p className="font-bold" style={{ color: 'var(--text-bright)' }}>{result.title}</p>
                      <p className="text-sm" style={{ color: 'var(--text-medium)' }}>{result.artist}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold" style={{ color: colors[index % 4] }}>
                      {Math.round(result.similarity_score * 100)}% match
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  )
}
