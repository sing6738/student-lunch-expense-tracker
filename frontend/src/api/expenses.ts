import { apiClient } from './client'
import type { ApiResponse } from '../types/api'
import type { Expense, ExpenseFormData, PaginatedResponse } from '../types/expense'

export const expensesApi = {
  list: (params?: any) => apiClient.get<PaginatedResponse<Expense>>('/expenses', { params }),
  get: (id: number) => apiClient.get<ApiResponse<Expense>>(`/expenses/${id}`),
  create: (data: ExpenseFormData) => apiClient.post<ApiResponse<{ id: number }>>('/expenses', data),
  createBatch: (data: { expenses: ExpenseFormData[] }) => apiClient.post<ApiResponse<{ ids: number[] }>>('/expenses/batch', data),
  update: (id: number, data: Partial<ExpenseFormData>) => apiClient.put<ApiResponse<{ id: number }>>(`/expenses/${id}`, data),
  delete: (id: number) => apiClient.delete<ApiResponse>(`/expenses/${id}`),
  exportCsv: () => apiClient.get('/expenses/export', { responseType: 'blob' }),
}
