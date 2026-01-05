import type { Metadata } from 'next'
import './globals.css'
import { Providers } from '@/components/providers'

export const metadata: Metadata = {
  title: 'Musigo',
  description: 'Discover music through AI-powered recommendations',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        {/* Subtle animated background layers (base + highlight masked to cursor) */}
        <div className="music-emoji-bg" aria-hidden="true">
          {/* Small, cryptic, music-related mnemonics and emoji */}
          <span className="emoji">♪</span>
          <span className="emoji">♫</span>
          <span className="emoji">♬</span>
          <span className="emoji">♩</span>
          <span className="emoji">🎵</span>
          <span className="emoji">🎶</span>
          <span className="emoji">🎧</span>
          <span className="emoji">🎷</span>
          <span className="emoji">🎸</span>
          <span className="emoji">🎹</span>
          <span className="emoji">🎺</span>
          <span className="emoji">📀</span>
          <span className="emoji">💿</span>
          <span className="emoji">🔊</span>
          <span className="emoji">🔉</span>
          <span className="emoji">▶</span>
          <span className="emoji">⏯</span>
          <span className="emoji">⏮</span>
          <span className="emoji">⏭</span>
          <span className="emoji">⏹</span>
          <span className="emoji">⏺</span>
          <span className="emoji">⏸</span>
          <span className="emoji">⏵</span>
          <span className="emoji">⏶</span>
          <span className="emoji">⏷</span>
          <span className="emoji">🔈</span>
          <span className="emoji">🔔</span>
          <span className="emoji">🎼</span>
          <span className="emoji">🎤</span>
          <span className="emoji">🎛️</span>
          <span className="emoji">🎚️</span>
          <span className="emoji">🎙️</span>
          <span className="emoji">📻</span>
          <span className="emoji">📡</span>
          <span className="emoji">🎞️</span>
          <span className="emoji">🎬</span>
          <span className="emoji">💽</span>
          <span className="emoji">📼</span>
          <span className="emoji">🎧</span>
          <span className="emoji">🎵</span>
          <span className="emoji">♭</span>
          <span className="emoji">♯</span>
          <span className="emoji">𝄞</span>
          <span className="emoji">𝄫</span>
          <span className="emoji">𝄪</span>
          <span className="emoji">🎼</span>
          <span className="emoji">🎧</span>
          <span className="emoji">🎶</span>
          <span className="emoji">🎵</span>
          <span className="emoji">🔈</span>
          <span className="emoji">🔊</span>
          <span className="emoji">🎙️</span>
          <span className="emoji">🎚️</span>
          <span className="emoji">🎛️</span>
          <span className="emoji">🎸</span>
          <span className="emoji">🎺</span>
          <span className="emoji">💿</span>
          <span className="emoji">📀</span>
          <span className="emoji">🎬</span>
          <span className="emoji">🎧</span>
          <span className="emoji">🎶</span>
          <span className="emoji">🎵</span>
          <span className="emoji">📻</span>
          <span className="emoji">🎼</span>
          <span className="emoji">🎷</span>
          <span className="emoji">🎹</span>
          <span className="emoji">🎸</span>
          <span className="emoji">🔊</span>
          <span className="emoji">🔉</span>
          <span className="emoji">🔈</span>
          <span className="emoji">💽</span>
          <span className="emoji">📼</span>
          <span className="emoji">▶</span>
          <span className="emoji">⏯</span>
          <span className="emoji">⏮</span>
          <span className="emoji">⏭</span>
          <span className="emoji">⏸</span>
        </div>
        <div className="music-emoji-bg music-emoji-bg--highlight" aria-hidden="true">
          {/* duplicated for highlight mask */}
          <span className="emoji">♪</span>
          <span className="emoji">♫</span>
          <span className="emoji">♬</span>
          <span className="emoji">♩</span>
          <span className="emoji">🎵</span>
          <span className="emoji">🎶</span>
          <span className="emoji">🎧</span>
          <span className="emoji">🎷</span>
          <span className="emoji">🎸</span>
          <span className="emoji">🎹</span>
          <span className="emoji">🎺</span>
          <span className="emoji">📀</span>
          <span className="emoji">💿</span>
          <span className="emoji">🔊</span>
          <span className="emoji">🔉</span>
          <span className="emoji">▶</span>
          <span className="emoji">⏯</span>
          <span className="emoji">⏮</span>
          <span className="emoji">⏭</span>
          <span className="emoji">⏹</span>
          <span className="emoji">⏺</span>
          <span className="emoji">⏸</span>
          <span className="emoji">⏵</span>
          <span className="emoji">⏶</span>
          <span className="emoji">⏷</span>
          <span className="emoji">🔈</span>
          <span className="emoji">🔔</span>
          <span className="emoji">🎼</span>
          <span className="emoji">🎤</span>
          <span className="emoji">🎛️</span>
          <span className="emoji">🎚️</span>
          <span className="emoji">🎙️</span>
          <span className="emoji">📻</span>
          <span className="emoji">📡</span>
          <span className="emoji">🎞️</span>
          <span className="emoji">🎬</span>
          <span className="emoji">💽</span>
          <span className="emoji">📼</span>
          <span className="emoji">🎧</span>
          <span className="emoji">🎵</span>
          <span className="emoji">♭</span>
          <span className="emoji">♯</span>
          <span className="emoji">𝄞</span>
          <span className="emoji">𝄫</span>
          <span className="emoji">𝄪</span>
          <span className="emoji">🎼</span>
          <span className="emoji">🎧</span>
          <span className="emoji">🎶</span>
          <span className="emoji">🎵</span>
          <span className="emoji">🔈</span>
          <span className="emoji">🔊</span>
          <span className="emoji">🎙️</span>
          <span className="emoji">🎚️</span>
          <span className="emoji">🎛️</span>
          <span className="emoji">🎸</span>
          <span className="emoji">🎺</span>
          <span className="emoji">💿</span>
          <span className="emoji">📀</span>
          <span className="emoji">🎬</span>
          <span className="emoji">🎧</span>
          <span className="emoji">🎶</span>
          <span className="emoji">🎵</span>
          <span className="emoji">📻</span>
          <span className="emoji">🎼</span>
          <span className="emoji">🎷</span>
          <span className="emoji">🎹</span>
          <span className="emoji">🎸</span>
          <span className="emoji">🔊</span>
          <span className="emoji">🔉</span>
          <span className="emoji">🔈</span>
          <span className="emoji">💽</span>
          <span className="emoji">📼</span>
          <span className="emoji">▶</span>
          <span className="emoji">⏯</span>
          <span className="emoji">⏮</span>
          <span className="emoji">⏭</span>
          <span className="emoji">⏸</span>
        </div>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function(){
                const root = document.documentElement;
                let pending = false;
                let lastX = window.innerWidth / 2;
                let lastY = window.innerHeight / 2;
                function apply(){
                  root.style.setProperty('--cursor-px-x', lastX + 'px');
                  root.style.setProperty('--cursor-px-y', lastY + 'px');
                  pending = false;
                }
                window.addEventListener('mousemove', (e) => {
                  lastX = e.clientX; lastY = e.clientY;
                  if(!pending){ pending = true; requestAnimationFrame(apply); }
                });
                // Initialize
                apply();
              })();
            `,
          }}
        />
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
