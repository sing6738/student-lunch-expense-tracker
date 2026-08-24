import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { BudgetSummary } from '@/types/budget'

export const useBudgetStore = defineStore('budget', () => {
  const summary = ref<BudgetSummary | null>(null)

  async function fetchBudgetSummary() {
    // TODO: API connection
  }

  return {
    summary,
    fetchBudgetSummary
  }
})
