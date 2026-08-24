import { defineStore } from 'pinia'
import { ref } from 'vue'
import { monthlyBudgetApi } from '@/api/monthlyBudget'
import type { MonthlyBudget, MonthlyBudgetSummary } from '@/types/monthlyBudget'

export const useMonthlyBudgetStore = defineStore('monthlyBudget', () => {
  const current = ref<MonthlyBudget | null>(null)
  const summary = ref<MonthlyBudgetSummary | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // year/month default to the current month on the backend when omitted,
  // so callers can just do fetchMonthlyBudget() for "this month".
  async function fetchMonthlyBudget(year?: number, month?: number) {
    loading.value = true
    error.value = null
    try {
      const res = await monthlyBudgetApi.get(year, month)
      current.value = res.data.data
      return current.value
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'โหลดงบประมาณรายเดือนไม่สำเร็จ'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function saveMonthlyBudget(data: Partial<MonthlyBudget>) {
    const res = await monthlyBudgetApi.update(data)
    // Refetch to get server-computed fields (total_fixed, remaining_for_variable)
    await fetchMonthlyBudget(data.year, data.month)
    return res.data.data
  }

  // Returns null (not throwing) when the user hasn't set up a budget for
  // that month yet — the backend returns 404 in that case, which is a
  // normal "not configured" state here, not an error to surface.
  async function fetchSummary(year?: number, month?: number) {
    loading.value = true
    error.value = null
    try {
      const res = await monthlyBudgetApi.getSummary(year, month)
      summary.value = res.data.data
      return summary.value
    } catch (err: any) {
      if (err.response?.status === 404) {
        summary.value = null
        return null
      }
      error.value = err.response?.data?.error?.message || 'โหลดสรุปงบประมาณไม่สำเร็จ'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    current,
    summary,
    loading,
    error,
    fetchMonthlyBudget,
    saveMonthlyBudget,
    fetchSummary
  }
})
