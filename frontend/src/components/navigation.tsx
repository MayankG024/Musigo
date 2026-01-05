'use client'

import { Music } from 'lucide-react'

export function Navigation() {
  // Auth removed: no logout; all features are public.

  return (
    <header className="glass border-b shadow-2xl relative z-20" style={{ borderColor: 'var(--glass-border)' }}>
      <div className="w-full px-6 md:px-10 lg:px-16 xl:px-24 2xl:px-32 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Music className="w-8 h-8" style={{ color: 'var(--spotify-green)' }} />
            <a href="/" className="text-2xl font-bold tracking-tight relative group" style={{
              background: 'linear-gradient(90deg, var(--spotify-green), var(--bright-cyan))',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              MUSIGO
              <span className="absolute left-0 -bottom-1 h-px w-0 bg-gradient-to-r from-[var(--spotify-green)] to-[var(--bright-cyan)] transition-all duration-300 group-hover:w-full" />
            </a>
          </div>
          
          <nav className="flex items-center space-x-6">
            <a href="/" className="font-medium transition-colors duration-200" style={{ color: 'var(--text-medium)' }} onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--spotify-green)'; }} onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-medium)'; }}>
              Home
            </a>
            <a href="/discover" className="font-medium transition-colors duration-200" style={{ color: 'var(--text-medium)' }} onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--spotify-green)'; }} onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-medium)'; }}>
              Discover
            </a>
            {
              <a href="/library" className="font-medium transition-colors duration-200" style={{ color: 'var(--text-medium)' }} onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--spotify-green)'; }} onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-medium)'; }}>
                My Library
              </a>
            }
            <a href="/trending" className="font-medium transition-colors duration-200" style={{ 
              color: 'var(--text-medium)' 
            }} onMouseEnter={(e) => {
              e.currentTarget.style.color = 'var(--spotify-green)';
            }} onMouseLeave={(e) => {
              e.currentTarget.style.color = 'var(--text-medium)';
            }}>
              Trending
            </a>
            
            {/* User Menu removed for public access mode */}
          </nav>
        </div>
      </div>
    </header>
  )
}
