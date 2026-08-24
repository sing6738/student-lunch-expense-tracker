import { defineStore } from 'pinia'
import { ref } from 'vue'
import { analyticsApi } from '@/api/analytics'
import type { AnalyticsSummary, AnalyticsTrend, AnalyticsCategory, AnalyticsCalendar } from '@/types/analytics'

export const useAnalyticsStore = defineStore('analytics', () => {
  const summary = ref<AnalyticsSummary | null>(null)
  const trend = ref<AnalyticsTrend | null>(null)
  const categories = ref<AnalyticsCategory[]>([])
  const calendar = ref<AnalyticsCalendar[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchSummary() {
    const res = await analyticsApi.getSummary()
    summary.value = res.data.data
    return summary.value
  }

  async function fetchTrend() {
    const res = await analyticsApi.getTrend()
    trend.value = res.data.data
    return trend.value
  }

  async function fetchCategories() {
    const res = await analyticsApi.getCategories()
    categories.value = res.data.data
    return categories.value
  }

  async function fetchCalendar() {
    const res = await analyticsApi.getCalendar()
    calendar.value = res.data.data
    return calendar.value
  }

  // Loads everything the Analytics/Dashboard views need in one go.
  // Runs in parallel and reports one shared loading/error state; if you
  // need to load just one chart's data, call that fetch*() directly instead.
  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      await Promise.all([fetchSummary(), fetchTrend(), fetchCategories(), fetchCalendar()])
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'โหลดข้อมูลวิเคราะห์ไม่สำเร็จ'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    summary,
    trend,
    categories,
    calendar,
    loading,
    error,
    fetchSummary,
    fetchTrend,
    fetchCategories,
    fetchCalendar,
    fetchAll
  }
})
