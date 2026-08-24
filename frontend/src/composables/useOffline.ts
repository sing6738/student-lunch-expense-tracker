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

export function useOffline() {
  const isOnline = ref(navigator.onLine)
  const toast = useToast()

  const updateOnlineStatus = () => {
    isOnline.value = navigator.onLine
    if (isOnline.value) {
      toast.add({ severity: 'success', summary: 'ออนไลน์', detail: 'กำลังเชื่อมต่ออินเทอร์เน็ต และซิงค์ข้อมูล', life: 3000 })
      syncOfflineData()
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

  async function saveExpenseOffline(expenseData: any) {
    await db.expenses.add({
      data: expenseData,
      createdAt: Date.now()
    })
    toast.add({ severity: 'info', summary: 'บันทึกออฟไลน์', detail: 'บันทึกข้อมูลเรียบร้อย จะซิงค์เมื่อมีอินเทอร์เน็ต', life: 3000 })
  }

  async function syncOfflineData() {
    const offlineItems = await db.expenses.toArray()
    if (offlineItems.length === 0) return

    // TODO: loop through offlineItems and POST to API
    // If successful, db.expenses.delete(item.id)
    console.log('Syncing items: ', offlineItems)
  }

  return {
    isOnline,
    saveExpenseOffline,
    syncOfflineData
  }
}
