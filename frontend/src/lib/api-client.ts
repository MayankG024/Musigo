import axios, { AxiosError, AxiosInstance } from 'axios'
import { ApiError } from '@/types/api'
import toast from 'react-hot-toast'

class ApiClient {
  private client: AxiosInstance
  private static instance: ApiClient

  private constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Public mode: no auth headers
    this.client.interceptors.request.use((config) => config)

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiError>) => {
        if (error.response) {
          const { status, data } = error.response
          
          // Handle specific error cases
          switch (status) {
            case 401:
              // Public mode: surface message, do not redirect
              toast.error(data?.detail || 'Unauthorized')
              break
            case 403:
              toast.error('You do not have permission to perform this action')
              break
            case 404:
              toast.error('Resource not found')
              break
            case 500:
              toast.error('Server error. Please try again later.')
              break
            default:
              toast.error(data?.detail || 'An error occurred')
          }
        } else if (error.request) {
          toast.error('Network error. Please check your connection.')
        } else {
          toast.error('An unexpected error occurred')
        }
        
        return Promise.reject(error)
      }
    )
  }

  public static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient()
    }
    return ApiClient.instance
  }

  // Auth token helpers removed in public mode

  // HTTP methods
  public async get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
    const response = await this.client.get<T>(url, { params })
    return response.data
  }

  public async post<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.post<T>(url, data)
    return response.data
  }

  public async put<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.put<T>(url, data)
    return response.data
  }

  public async patch<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.patch<T>(url, data)
    return response.data
  }

  public async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<T>(url)
    return response.data
  }
}

export const apiClient = ApiClient.getInstance()
export default apiClient
