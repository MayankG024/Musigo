import apiClient from '../api-client'
import { AuthResponse, LoginRequest, RegisterRequest, User } from '@/types/api'

export const authApi = {
  async login(data: LoginRequest): Promise<AuthResponse> {
    // Public access mode: no token storage needed
    // Use /login/json endpoint for JSON payload (vs OAuth2 form-encoded /login)
    const response = await apiClient.post<AuthResponse>('/api/auth/login/json', data)
    return response
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    // Public access mode: no token storage needed
    const response = await apiClient.post<AuthResponse>('/api/auth/register', data)
    return response
  },

  async logout(): Promise<void> {
    // Public access mode: logout is a no-op
    await apiClient.post('/api/auth/logout')
  },

  async getCurrentUser(): Promise<User> {
    // Public access mode: returns demo user
    return apiClient.get<User>('/api/auth/me')
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    return apiClient.patch<User>('/api/auth/profile', data)
  },
}
