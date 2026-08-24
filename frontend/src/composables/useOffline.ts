import Dexie, { type Table } from 'dexie'
import { ref, onMounted, onUnmounted } from 'vue'
import { useToast } from 'primevue/usetoast'

interface OfflineExpense {
  id?: number;
  data: any;
  createdAt: number;
}

class LunchExpenseDB extends Dexie {
  expenses!: Table<OfflineExpense>

  constructor() {
    super('LunchExpenseDB')
    this.version(1).stores({
      expenses: '++id, createdAt'
    })
  }
}

const db = new LunchExpenseDB()

// Plain (non-lifecycle) helpers — safe to import from a Pinia store or
// anywhere outside a component's setup(), since they don't touch
// onMounted/onUnmounted.
export async function saveExpenseOffline(expenseData: any) {
  await db.expenses.add({
    data: expenseData,
    createdAt: Date.now()
  })
}

export async function getOfflineQueue() {
  return db.expenses.toArray()
}

export async function getOfflineQueueCount() {
  return db.expenses.count()
}

// Runs the queued expenses through a provided "create" function (usually
// expensesApi.create) and drops each item from the queue once it succeeds.
// Stops and keeps the remaining items queued on the first failure so a
// flaky connection doesn't drop data.
export async function syncOfflineData(createFn: (data: any) => Promise<unknown>) {
  const offlineItems = await db.expenses.toArray()
  let synced = 0
  for (const item of offlineItems) {
    try {
      await createFn(item.data)
      await db.expenses.delete(item.id!)
      synced++
    } catch (err) {
      break
    }
  }
  return { synced, remaining: offlineItems.length - synced }
}

// Component-facing composable: online/offline toasts + delegates to the
// plain helpers above. Only use this inside a component's setup().
export function useOffline() {
  const isOnline = ref(navigator.onLine)
  const toast = useToast()

  const updateOnlineStatus = () => {
    isOnline.value = navigator.onLine
    if (isOnline.value) {
      toast.add({ severity: 'success', summary: 'ออนไลน์', detail: 'กำลังเชื่อมต่ออินเทอร์เน็ต และซิงค์ข้อมูล', life: 3000 })
    } else {
      toast.add({ severity: 'warn', summary: 'ออฟไลน์', detail: 'ข้อมูลจะถูกเก็บไว้ชั่วคราวและบันทึกเมื่อเชื่อมต่ออินเทอร์เน็ตอีกครั้ง', life: 3000 })
    }
  }

  onMounted(() => {
    window.addEventListener('online', updateOnlineStatus)
    window.addEventListener('offline', updateOnlineStatus)
  })

  onUnmounted(() => {
    window.removeEventListener('online', updateOnlineStatus)
    window.removeEventListener('offline', updateOnlineStatus)
  })

  return {
    isOnline,
    saveExpenseOffline,
    syncOfflineData,
    getOfflineQueue,
    getOfflineQueueCount
  }
}
