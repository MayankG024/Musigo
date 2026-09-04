import apiClient from '../api-client'
import { 
  Favorite, 
  SearchHistory,
  PaginatedResponse,
  Song
} from '@/types/api'

export const userApi = {
  // Favorites
  async getFavorites(page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<Favorite>> {
    return apiClient.get<PaginatedResponse<Favorite>>('/api/user/favorites', { 
      page, 
      page_size: pageSize 
    })
  },

  async addFavorite(songId: string): Promise<Favorite> {
    return apiClient.post<Favorite>(`/api/user/favorites/${songId}`)
  },

  async removeFavorite(songId: string): Promise<void> {
    return apiClient.delete(`/api/user/favorites/${songId}`)
  },

  async isFavorite(songId: string): Promise<boolean> {
    try {
      await apiClient.get(`/api/user/favorites/${songId}/check`)
      return true
    } catch {
      return false
    }
  },

  // Search History
  async getSearchHistory(page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<SearchHistory>> {
    return apiClient.get<PaginatedResponse<SearchHistory>>('/api/user/history', { 
      page, 
      page_size: pageSize 
    })
  },

  async clearSearchHistory(): Promise<void> {
    return apiClient.delete('/api/user/history')
  },

  // Recently Played
  async getRecentlyPlayed(limit: number = 20): Promise<Song[]> {
    return apiClient.get<Song[]>('/api/user/recently-played', { limit })
  },

  async addToRecentlyPlayed(songId: string): Promise<void> {
    return apiClient.post(`/api/user/recently-played/${songId}`)
  },

  // User Stats
  async getUserStats(): Promise<{
    favorites_count: number
    playlists_count: number
    total_listening_time: number
    top_genres: string[]
    top_artists: string[]
  }> {
    return apiClient.get('/api/user/stats')
  },
}
