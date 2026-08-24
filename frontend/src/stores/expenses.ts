import { defineStore } from 'pinia'
import { ref } from 'vue'
import { expensesApi } from '@/api/expenses'
import { saveExpenseOffline, syncOfflineData, getOfflineQueueCount } from '@/composables/useOffline'
import type { Expense, ExpenseFilters, ExpenseFormData, PaginatedResponse } from '@/types/expense'

export const useExpensesStore = defineStore('expenses', () => {
  const expenses = ref<Expense[]>([])
  const meta = ref<PaginatedResponse<Expense>['meta'] | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Number of expenses currently queued offline, waiting to sync.
  // Refresh this after addExpense() / syncQueue() to drive a "pending" badge.
  const offlineQueueCount = ref(0)

  async function refreshOfflineQueueCount() {
    offlineQueueCount.value = await getOfflineQueueCount()
  }

  async function fetchExpenses(filters: ExpenseFilters = {}) {
    loading.value = true
    error.value = null
    try {
      const res = await expensesApi.list(filters)
      expenses.value = res.data.data
      meta.value = res.data.meta
      return res.data
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'โหลดรายการไม่สำเร็จ'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Tries the network first; if the request fails because the device is
  // offline (no response reaches the server), the expense is queued in
  // IndexedDB instead of being lost. Returns whether it was saved online
  // or queued, so the caller can show the right toast.
  async function addExpense(data: ExpenseFormData): Promise<'online' | 'offline'> {
    try {
      await expensesApi.create(data)
      return 'online'
    } catch (err: any) {
      if (!err.response) {
        // No response = network/connectivity failure, not a validation error
        await saveExpenseOffline(data)
        await refreshOfflineQueueCount()
        return 'offline'
      }
      throw err
    }
  }

  async function addExpensesBatch(items: ExpenseFormData[]) {
    const res = await expensesApi.createBatch({ expenses: items })
    return res.data.data?.ids || []
  }

  async function updateExpense(id: number, data: Partial<ExpenseFormData>) {
    const res = await expensesApi.update(id, data)
    return res.data.data
  }

  async function deleteExpense(id: number) {
    await expensesApi.delete(id)
    expenses.value = expenses.value.filter(e => e.id !== id)
  }

  async function exportCsv() {
    const res = await expensesApi.exportCsv()
    return res.data as Blob
  }

  // Replays anything queued while offline. Call this on the 'online'
  // window event or when the app resumes to foreground — iOS Safari does
  // not support the Background Sync API, so this can't run in the
  // background and must be triggered while the app is actually open.
  async function syncQueue() {
    const result = await syncOfflineData((data) => expensesApi.create(data))
    await refreshOfflineQueueCount()
    return result
  }

  return {
    expenses,
    meta,
    loading,
    error,
    offlineQueueCount,
    refreshOfflineQueueCount,
    fetchExpenses,
    addExpense,
    addExpensesBatch,
    updateExpense,
    deleteExpense,
    exportCsv,
    syncQueue
  }
})
