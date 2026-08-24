import { defineStore } from 'pinia'
import { ref } from 'vue'
import { budgetApi } from '@/api/budget'
import type { BudgetSummary } from '@/types/budget'

export const useBudgetStore = defineStore('budget', () => {
  const summary = ref<BudgetSummary | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchBudgetSummary() {
    loading.value = true
    error.value = null
    try {
      const res = await budgetApi.getSummary()
      summary.value = res.data.data
      return summary.value
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'โหลดข้อมูลงบประมาณไม่สำเร็จ'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateBudget(dailyBudget: number) {
    await budgetApi.update({ daily_budget: dailyBudget })
    // Refetch so `summary` (spent_today, remaining_today, is_over_budget)
    // stays consistent instead of only patching daily_budget locally.
    await fetchBudgetSummary()
  }

  return {
    summary,
    loading,
    error,
    fetchBudgetSummary,
    updateBudget
  }
})
