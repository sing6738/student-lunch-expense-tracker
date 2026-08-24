import { apiClient } from './client'
import type { ApiResponse } from '../types/api'
import type { OnlineOrder, OnlineOrderFormData } from '../types/order'

export const ordersApi = {
  list: () => apiClient.get<ApiResponse<OnlineOrder[]>>('/orders'),
  create: (data: OnlineOrderFormData) => apiClient.post<ApiResponse<{ id: number }>>('/orders', data),
  update: (id: number, data: Partial<OnlineOrderFormData>) => apiClient.put<ApiResponse<{ id: number }>>(`/orders/${id}`, data),
  delete: (id: number) => apiClient.delete<ApiResponse>(`/orders/${id}`),
}
