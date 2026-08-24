import { apiClient } from './client'
import type { ApiResponse } from '../types/api'
import type { AnalyticsSummary, AnalyticsTrend, AnalyticsCategory, AnalyticsCalendar } from '../types/analytics'

export const analyticsApi = {
  getSummary: () => apiClient.get<ApiResponse<AnalyticsSummary>>('/analytics/summary'),
  getTrend: () => apiClient.get<ApiResponse<AnalyticsTrend>>('/analytics/trend'),
  getCategories: () => apiClient.get<ApiResponse<AnalyticsCategory[]>>('/analytics/categories'),
  getCalendar: () => apiClient.get<ApiResponse<AnalyticsCalendar[]>>('/analytics/calendar'),
}
