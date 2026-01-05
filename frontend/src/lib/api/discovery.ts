import apiClient from '../api-client'
import { 
  DiscoveryRequest, 
  DiscoveryResult, 
  RecommendationRequest, 
  Recommendation,
  Song 
} from '@/types/api'

export const discoveryApi = {
  async discover(request: DiscoveryRequest): Promise<DiscoveryResult[]> {
    return apiClient.post<DiscoveryResult[]>('/api/discovery/discover', request)
  },

  async getRecommendations(request: RecommendationRequest): Promise<Recommendation[]> {
    return apiClient.post<Recommendation[]>('/api/recommendations/recommend', request)
  },

  async getSimilarSongs(songId: string, limit: number = 10): Promise<Song[]> {
    return apiClient.get<Song[]>(`/api/discovery/similar/${songId}`, { limit })
  },

  async getTrendingSongs(limit: number = 20): Promise<Song[]> {
    return apiClient.get<Song[]>('/api/discovery/trending', { limit })
  },

  async getGenres(): Promise<string[]> {
    return apiClient.get<string[]>('/api/discovery/genres')
  },

  async searchSongs(query: string, limit: number = 20): Promise<Song[]> {
    return apiClient.get<Song[]>('/api/songs/search', { q: query, limit })
  },

  async getSongById(songId: string): Promise<Song> {
    return apiClient.get<Song>(`/api/songs/${songId}`)
  },
}
