import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Expense, ExpenseFilters, PaginatedResponse } from '@/types/expense'

export const useExpensesStore = defineStore('expenses', () => {
  const expenses = ref<Expense[]>([])
  
  // Offline queue for PWA (Task 10/11)
  const offlineQueue = ref<any[]>([])

  async function fetchExpenses(filters: ExpenseFilters) {
    // TODO: Connect to API
    return { data: [], meta: { page: 1, per_page: 10, total: 0, total_pages: 0 } }
  }

  async function addExpense(expense: any) {
    // TODO: Connect to API or offline queue
  }

  return {
    expenses,
    offlineQueue,
    fetchExpenses,
    addExpense
  }
})
