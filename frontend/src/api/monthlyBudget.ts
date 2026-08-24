import { apiClient } from './client'
import type { ApiResponse } from '../types/api'
import type { MonthlyBudget, MonthlyBudgetSummary } from '../types/monthlyBudget'

export const monthlyBudgetApi = {
  get: (year?: number, month?: number) => 
    apiClient.get<ApiResponse<MonthlyBudget | null>>('/monthly-budget', { params: { year, month } }),
    
  update: (data: Partial<MonthlyBudget>) => 
    apiClient.put<ApiResponse<{ id: number }>>('/monthly-budget', data),
    
  getSummary: (year?: number, month?: number) => 
    apiClient.get<ApiResponse<MonthlyBudgetSummary>>('/monthly-budget/summary', { params: { year, month } }),
}
