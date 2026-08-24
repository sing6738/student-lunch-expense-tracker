import { apiClient } from './client'
import type { ApiResponse } from '../types/api'
import type { User } from '../types/auth'

export const profileApi = {
  get: () => apiClient.get<ApiResponse<User>>('/profile'),
  update: (data: Partial<User> & { password?: string }) => apiClient.put<ApiResponse>('/profile', data),
}
