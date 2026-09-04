"use client";

import React from 'react';

const SONGS = [
  "Bohemian Rhapsody",
  "Imagine",
  "Hey Jude",
  "Hotel California",
  "Stairway to Heaven",
  "Smells Like Teen Spirit",
  "Billie Jean",
  "Like a Rolling Stone",
  "Wonderwall",
  "Shape of You",
  "Let It Be",
  "Sweet Child O' Mine",
  "Rolling in the Deep",
  "Uptown Funk",
  "Livin' on a Prayer",
  "Blinding Lights",
  "Dance Monkey",
  "Bad Guy",
  "Levitating",
  "Peaches",
  "Old Town Road",
  "Someone Like You",
  "Thinking Out Loud",
  "Shake It Off",
  "Hello",
  "Closer",
  "God's Plan",
  "Despacito",
  "Havana",
  "Rockstar",
  "Sunflower",
  "Believer",
  "Perfect",
  "Señorita",
];

// Duplicate list for seamless looping
const loop = [...SONGS, ...SONGS];

export function EdgeMarquee() {
  return (
    <div className="edge-marquee pointer-events-none select-none" aria-hidden="true">
      {/* Top */}
      <div className="edge-marquee-strip horizontal top">
        <div className="edge-marquee-track">
          {loop.map((t, i) => (
            <span key={i} className="edge-marquee-item">{t}</span>
          ))}
        </div>
      </div>
      {/* Bottom */}
      <div className="edge-marquee-strip horizontal bottom">
        <div className="edge-marquee-track reverse">
          {loop.map((t, i) => (
            <span key={i} className="edge-marquee-item">{t}</span>
          ))}
        </div>
      </div>
      {/* Left */}
      <div className="edge-marquee-strip vertical left">
        <div className="edge-marquee-track-vertical">
          {loop.map((t, i) => (
            <span key={i} className="edge-marquee-item vertical-item">{t}</span>
          ))}
        </div>
      </div>
      {/* Right */}
      <div className="edge-marquee-strip vertical right">
        <div className="edge-marquee-track-vertical reverse">
          {loop.map((t, i) => (
            <span key={i} className="edge-marquee-item vertical-item">{t}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default EdgeMarquee;
