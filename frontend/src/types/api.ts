// User types
export interface User {
  id: string
  email: string
  username: string
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
}

// Song types
export interface Song {
  song_id: string
  title: string
  artist: string
  album?: string
  genre?: string
  year?: number
  duration?: number
  preview_url?: string
  album_art_url?: string
  spotify_id?: string
  features?: AudioFeatures
}

export interface AudioFeatures {
  tempo: number
  energy: number
  danceability: number
  valence: number
  acousticness: number
  instrumentalness: number
  speechiness: number
  loudness: number
}

// Discovery types
export interface DiscoveryRequest {
  query: string
  limit?: number
  filter_genre?: string
  min_year?: number
  max_year?: number
}

export interface DiscoveryResult extends Song {
  similarity_score: number
  explanation?: string
}

// Playlist types
export interface Playlist {
  id: string
  user_id: string
  name: string
  description?: string
  is_public: boolean
  created_at: string
  updated_at: string
  songs?: Song[]
  song_count?: number
}

export interface CreatePlaylistRequest {
  name: string
  description?: string
  is_public?: boolean
}

export interface UpdatePlaylistRequest {
  name?: string
  description?: string
  is_public?: boolean
}

// Recommendation types
export interface RecommendationRequest {
  seed_songs?: string[]
  seed_artists?: string[]
  seed_genres?: string[]
  limit?: number
  audio_features?: Partial<AudioFeatures>
}

export interface Recommendation extends Song {
  reason: string
  score: number
}

// Search History
export interface SearchHistory {
  id: string
  user_id: string
  query: string
  results_count: number
  created_at: string
}

// Favorites
export interface Favorite {
  id: string
  user_id: string
  song_id: string
  song: Song
  created_at: string
}

// API Error
export interface ApiError {
  detail: string
  status_code?: number
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}
