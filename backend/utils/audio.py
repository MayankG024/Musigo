"""Utilities for music metadata and audio feature extraction"""

from typing import Dict, Any, Optional
import os
import librosa
import mutagen
from mutagen.easyid3 import EasyID3


def extract_audio_features(file_path: str) -> Dict[str, Any]:
    """Extract basic audio features using librosa"""
    try:
        y, sr = librosa.load(file_path)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        rmse = librosa.feature.rms(y=y).mean()
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr).mean()
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y).mean()
        
        # Normalize some features to 0-1 range
        energy = min(max(rmse * 10, 0), 1)
        brightness = min(max(spectral_centroid / 8000, 0), 1)
        
        return {
            "tempo": float(tempo),
            "energy": float(energy),
            "brightness": float(brightness),
            "zero_crossing_rate": float(zero_crossing_rate),
        }
    except Exception as e:
        return {"error": str(e)}


def extract_metadata(file_path: str) -> Dict[str, Any]:
    """Extract basic metadata from audio file"""
    try:
        file = mutagen.File(file_path, easy=True)
        if not file:
            return {}
        metadata = {}
        
        # Extract common tags
        for tag in ["title", "artist", "album", "genre"]:
            if tag in file:
                metadata[tag] = file[tag][0] if isinstance(file[tag], list) else file[tag]
        
        # Duration
        metadata["duration_seconds"] = getattr(file.info, "length", None)
        
        return metadata
    except Exception as e:
        return {"error": str(e)}

