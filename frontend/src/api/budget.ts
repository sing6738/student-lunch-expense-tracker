import { apiClient } from './client'
import type { ApiResponse } from '../types/api'
import type { BudgetSummary } from '../types/budget'

export const budgetApi = {
  getSummary: () => apiClient.get<ApiResponse<BudgetSummary>>('/budget'),
  update: (data: { daily_budget: number }) => apiClient.put<ApiResponse>('/budget', data),
}
