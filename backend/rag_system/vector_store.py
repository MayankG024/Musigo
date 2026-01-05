"""Vector store for music embeddings using ChromaDB (optional).

This module is resilient when embeddings are disabled or ChromaDB isn't
installed. It returns empty results in that case so the API can run without
heavy native dependencies on Windows.
"""

from typing import List, Dict, Any, Optional
import os
import json
try:
    import numpy as np
except Exception:  # numpy is listed in optional requirements
    np = None  # type: ignore
from api.core.config import settings as app_settings

# Feature flag: allow disabling embeddings entirely via env
EMBEDDINGS_DISABLED = os.getenv("DISABLE_EMBEDDINGS", "false").lower() in {"1", "true", "yes"}

# Try optional imports; tolerate absence when disabled
chromadb = None
ChromaSettings = None
HttpClient = None
if not EMBEDDINGS_DISABLED:
    try:
        import chromadb  # type: ignore
        from chromadb.config import Settings as ChromaSettings  # type: ignore
        from chromadb import HttpClient  # type: ignore
    except Exception:
        chromadb = None
        ChromaSettings = None
        HttpClient = None

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:
    SentenceTransformer = None  # type: ignore


class MusicVectorStore:
    """Manages music embeddings and similarity search"""
    
    def __init__(self):
        self.collection = None
        self.model = None  # lazy
        self.use_fallback_embeddings = False
        self.embeddings_disabled = EMBEDDINGS_DISABLED or (chromadb is None or (ChromaSettings is None and HttpClient is None))
        if not self.embeddings_disabled and chromadb:
            http_url = os.getenv("CHROMA_HTTP_URL")
            if http_url:
                # Force HTTP client when URL is provided to avoid mixed backends
                try:
                    scheme, rest = http_url.split("://", 1) if "://" in http_url else ("http", http_url)
                    host_part = rest
                    port = 8000
                    if ":" in rest:
                        host_part, port_str = rest.rsplit(":", 1)
                        try:
                            port = int(port_str)
                        except ValueError:
                            port = 8000
                    use_ssl = scheme == "https"
                    # Prefer attribute access to avoid import shape issues
                    http_cls = getattr(chromadb, "HttpClient", None)
                    if http_cls is None:
                        raise RuntimeError("Chroma HttpClient not available")
                    self.client = http_cls(host=host_part, port=port, ssl=use_ssl)
                    print(f"🔗 Using Chroma HTTP client at {host_part}:{port} (ssl={use_ssl})")
                except Exception as e:
                    # Do not silently fall back; mark embeddings disabled for clarity
                    print(f"⚠️ Failed to initialize Chroma HTTP client: {e}")
                    self.client = None
                    self.embeddings_disabled = True
            elif ChromaSettings is not None:
                self.client = chromadb.PersistentClient(
                    path=app_settings.CHROMA_PERSIST_DIR,
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
                print(f"💾 Using Chroma persistent client at {app_settings.CHROMA_PERSIST_DIR}")
            else:
                self.client = None
        else:
            self.client = None
    
    async def initialize(self):
        """Initialize or get the music collection"""
        if self.embeddings_disabled or not self.client:
            return
        try:
            self.collection = self.client.get_or_create_collection(
                name="music_embeddings",
                metadata={"description": "Music metadata and feature embeddings"}
            )
            print(f"✅ ChromaDB collection initialized successfully")
        except Exception as e:
            print(f"⚠️ ChromaDB initialization failed: {e}")
            print(f"   Continuing without vector store - semantic search disabled")
            self.embeddings_disabled = True
            self.collection = None
    
    def _ensure_model(self):
        if self.embeddings_disabled:
            raise RuntimeError("Embeddings disabled or unavailable (ChromaDB not installed)")
        if self.model is None and not self.use_fallback_embeddings:
            if SentenceTransformer is None:
                # Fallback to deterministic hash-based embeddings
                self.use_fallback_embeddings = True
                return
            try:
                self.model = SentenceTransformer(app_settings.EMBEDDING_MODEL)
            except Exception:
                # If model cannot be loaded (e.g., no internet), fallback
                self.use_fallback_embeddings = True
                self.model = None

    def _fallback_embed(self, text: str, dim: int = 384) -> List[float]:
        """Deterministic embedding using a hash-based RNG. For demo/offline use only."""
        import hashlib
        if np is None:
            raise RuntimeError("NumPy not available for fallback embeddings")
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # Seed RNG from hash bytes
        seed = int.from_bytes(h[:8], byteorder="little", signed=False)
        rng = np.random.default_rng(seed)
        vec = rng.normal(loc=0.0, scale=1.0, size=(dim,))
        # Normalize to unit length
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.astype(float).tolist()

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        self._ensure_model()
        if self.use_fallback_embeddings or self.model is None:
            return self._fallback_embed(text)
        return self.model.encode(text).tolist()
    
    def create_music_text(self, song_data: Dict[str, Any]) -> str:
        """Create searchable text from song metadata"""
        parts = [
            f"Title: {song_data.get('title', '')}",
            f"Artist: {song_data.get('artist', '')}",
            f"Album: {song_data.get('album', '')}",
            f"Genres: {', '.join(song_data.get('genres', []))}",
            f"Tags: {', '.join(song_data.get('tags', []))}",
            f"Mood: {song_data.get('mood', '')}",
        ]
        
        # Add audio features if available
        if 'energy' in song_data:
            parts.append(f"Energy: {'high' if song_data['energy'] > 0.7 else 'medium' if song_data['energy'] > 0.4 else 'low'}")
        if 'valence' in song_data:
            parts.append(f"Mood: {'happy' if song_data['valence'] > 0.7 else 'neutral' if song_data['valence'] > 0.4 else 'sad'}")
        if 'danceability' in song_data:
            parts.append(f"Danceability: {'high' if song_data['danceability'] > 0.7 else 'medium' if song_data['danceability'] > 0.4 else 'low'}")
        
        # Add lyrics snippet if available
        if song_data.get('lyrics'):
            parts.append(f"Lyrics: {song_data['lyrics'][:200]}")
        
        return " ".join(parts)
    
    async def add_song(self, song_id: str, song_data: Dict[str, Any]):
        """Add a song to the vector store"""
        if self.embeddings_disabled:
            return []
        if not self.collection:
            await self.initialize()
            if self.embeddings_disabled or not self.collection:
                return []
        
        text = self.create_music_text(song_data)
        embedding = self.generate_embedding(text)
        try:
            print(f"➕ Indexing song into Chroma id={song_id} title={song_data.get('title','')}")
        except Exception:
            pass
        
        # Store in ChromaDB
        self.collection.add(
            ids=[song_id],
            embeddings=[embedding],
            metadatas=[{
                "song_id": song_id,
                "title": song_data.get("title", ""),
                "artist": song_data.get("artist", ""),
                "genres": json.dumps(song_data.get("genres", [])),
                "energy": song_data.get("energy", 0.5),
                "valence": song_data.get("valence", 0.5),
                "danceability": song_data.get("danceability", 0.5),
            }],
            documents=[text]
        )
    
    async def search_similar(
        self, 
        query: str, 
        n_results: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar songs based on query"""
        if self.embeddings_disabled:
            return []
        if not self.collection:
            await self.initialize()
            if self.embeddings_disabled or not self.collection:
                return []
        
        query_embedding = self.generate_embedding(query)
        
        # Perform search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_dict
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "document": results['documents'][0][i] if results['documents'] else ""
                })
        
        return formatted_results
    
    async def get_recommendations(
        self,
        song_ids: List[str],
        n_recommendations: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recommendations based on multiple songs"""
        if self.embeddings_disabled:
            return []
        if not self.collection:
            await self.initialize()
            if self.embeddings_disabled or not self.collection:
                return []
        
        # Get embeddings for input songs (ensure embeddings are included over HTTP client)
        song_data = self.collection.get(ids=song_ids, include=["embeddings"])  # type: ignore[arg-type]
        
        if not song_data['embeddings']:
            return []
        
        # Average the embeddings
        if np is None:
            raise RuntimeError("NumPy not available; install optional requirements to enable recommendations")
        avg_embedding = np.mean(song_data['embeddings'], axis=0).tolist()
        
        # Find similar songs
        results = self.collection.query(
            query_embeddings=[avg_embedding],
            n_results=n_recommendations + len(song_ids),  # Get extra to filter out input songs
        )
        
        # Format and filter results
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                if results['ids'][0][i] not in song_ids:
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "distance": results['distances'][0][i] if results['distances'] else None,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    })
                    if len(formatted_results) >= n_recommendations:
                        break
        
        return formatted_results


# Global instance
vector_store = MusicVectorStore()


async def init_vector_store():
    """Initialize the vector store"""
    await vector_store.initialize()
    print("✅ Vector store initialized")
