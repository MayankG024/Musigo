"use client";
import React, { useMemo } from 'react';

const SONGS = [
  'Bohemian Rhapsody',
  'Imagine',
  'Hey Jude',
  'Hotel California',
  'Stairway to Heaven',
  'Smells Like Teen Spirit',
  'Billie Jean',
  'Like a Rolling Stone',
  'Wonderwall',
  'Shape of You',
  'Let It Be',
  'Sweet Child O\' Mine',
  'Rolling in the Deep',
  'Uptown Funk',
  'Livin\' on a Prayer',
  'Blinding Lights', 
  'Wish You Were Here',
  'Bad Guy',
  'Levitating',
  'Emptiness Machine',
  'Old Town Road',
  'Someone Like You',
  'Thinking Out Loud',
  'Shake It Off',
  'Hello',
  'My Way',
  'God\'s Plan',
  'Rolling in the Deep',
  'Despacito',
  'Havana',
  'Rockstar',
  'Sunflower',
  'Believer',
  'Perfect',
  'Dancing Queen',
];

interface SongMarqueeProps { onSongClick?: (title: string) => void }

export function SongMarquee({ onSongClick }: SongMarqueeProps) {
  // Triple duplication to ensure seamless loop without gaps at slower speed
  const loop = useMemo(() => [...SONGS, ...SONGS, ...SONGS], []);
  return (
  <div className="marquee-wrapper wide">
      <div className="marquee-shell group">
        <div className="marquee-track reverse slow">
          {loop.map((title, i) => (
            <div className="marquee-item" key={i}>
              <button aria-label={title} onClick={() => onSongClick?.(title)}>{title}</button>
              <div className="marquee-pop">{title}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default SongMarquee;
