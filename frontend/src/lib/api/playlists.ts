import apiClient from '../api-client'
import { 
  Playlist, 
  CreatePlaylistRequest, 
  UpdatePlaylistRequest,
  PaginatedResponse,
  Song
} from '@/types/api'

export const playlistApi = {
  async getMyPlaylists(page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<Playlist>> {
    return apiClient.get<PaginatedResponse<Playlist>>('/api/playlists/my', { 
      page, 
      page_size: pageSize 
    })
  },

  async getPublicPlaylists(page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<Playlist>> {
    return apiClient.get<PaginatedResponse<Playlist>>('/api/playlists/public', { 
      page, 
      page_size: pageSize 
    })
  },

  async getPlaylistById(playlistId: string): Promise<Playlist> {
    return apiClient.get<Playlist>(`/api/playlists/${playlistId}`)
  },

  async createPlaylist(data: CreatePlaylistRequest): Promise<Playlist> {
    return apiClient.post<Playlist>('/api/playlists', data)
  },

  async updatePlaylist(playlistId: string, data: UpdatePlaylistRequest): Promise<Playlist> {
    return apiClient.patch<Playlist>(`/api/playlists/${playlistId}`, data)
  },

  async deletePlaylist(playlistId: string): Promise<void> {
    return apiClient.delete(`/api/playlists/${playlistId}`)
  },

  async addSongToPlaylist(playlistId: string, songId: string): Promise<Playlist> {
    return apiClient.post<Playlist>(`/api/playlists/${playlistId}/songs/${songId}`)
  },

  async removeSongFromPlaylist(playlistId: string, songId: string): Promise<Playlist> {
    return apiClient.delete<Playlist>(`/api/playlists/${playlistId}/songs/${songId}`)
  },

  async getPlaylistSongs(playlistId: string): Promise<Song[]> {
    return apiClient.get<Song[]>(`/api/playlists/${playlistId}/songs`)
  },

  async reorderPlaylistSongs(playlistId: string, songIds: string[]): Promise<Playlist> {
    return apiClient.put<Playlist>(`/api/playlists/${playlistId}/reorder`, { song_ids: songIds })
  },
}
