import { apiClient } from './client'
import type { ApiResponse } from '../types/api'
import type { User } from '../types/auth'

export const authApi = {
  login: (data: any) => apiClient.post<ApiResponse<{ token: string, user: User }>>('/auth/login', data),
  register: (data: any) => apiClient.post<ApiResponse>('/auth/register', data),
  logout: () => apiClient.post<ApiResponse>('/auth/logout'),
  refresh: () => apiClient.post<ApiResponse<{ token: string }>>('/auth/refresh'),
  getMe: () => apiClient.get<ApiResponse<User>>('/auth/me'),
}
