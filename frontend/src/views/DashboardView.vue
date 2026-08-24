<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useBudgetStore } from '../stores/budget'
import { useAnalyticsStore } from '../stores/analytics'
import { useExpensesStore } from '../stores/expenses'
import { useFormat } from '../composables/useFormat'

import Button from 'primevue/button'
import Card from 'primevue/card'
import ProgressBar from 'primevue/progressbar'

const router = useRouter()
const { formatTHB } = useFormat()
const authStore = useAuthStore()
const budgetStore = useBudgetStore()
const analyticsStore = useAnalyticsStore()
const expensesStore = useExpensesStore()

onMounted(async () => {
  await Promise.all([
    budgetStore.fetchBudgetSummary(),
    analyticsStore.fetchAll(),
    expensesStore.fetchExpenses({ per_page: 5 })
  ])
})

const budgetProgress = computed(() => {
  if (!budgetStore.summary || budgetStore.summary.daily_budget <= 0) return 0
  return Math.min((budgetStore.summary.spent_today / budgetStore.summary.daily_budget) * 100, 100)
})
</script>

<template>
  <div class="p-4 max-w-4xl mx-auto flex flex-col gap-6">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">สวัสดี, {{ authStore.user?.username }}</h1>
        <p class="text-gray-500 text-sm">สรุปการใช้จ่ายวันนี้</p>
      </div>
      <Button icon="pi pi-plus" label="เพิ่มรายจ่าย" @click="router.push('/expenses/add')" />
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Card>
        <template #title>
          <div class="flex items-center gap-2">
            <i class="pi pi-wallet text-primary text-xl"></i> 
            ยอดใช้จ่ายวันนี้
          </div>
        </template>
        <template #content>
          <div class="text-4xl font-bold text-gray-800 my-2">
            {{ formatTHB(budgetStore.summary?.spent_today || 0) }}
          </div>
          <div class="text-sm text-gray-500 mb-4">
            งบประมาณต่อวัน: {{ formatTHB(budgetStore.summary?.daily_budget || 0) }}
          </div>
          <ProgressBar :value="budgetProgress" :showValue="false" 
            :class="budgetStore.summary?.is_over_budget ? 'p-progressbar-danger' : 'p-progressbar-success'" />
          <div class="flex justify-between text-xs mt-2" :class="budgetStore.summary?.is_over_budget ? 'text-red-500' : 'text-green-600'">
            <span>{{ budgetStore.summary?.is_over_budget ? 'เกินงบประมาณแล้ว!' : 'ยังอยู่ในงบ' }}</span>
            <span>เหลือ: {{ formatTHB(budgetStore.summary?.remaining_today || 0) }}</span>
          </div>
        </template>
      </Card>
      
      <Card>
        <template #title>
          <div class="flex items-center gap-2">
            <i class="pi pi-calendar text-primary text-xl"></i>
            สรุปเดือนนี้
          </div>
        </template>
        <template #content>
          <div class="flex flex-col gap-4">
            <div>
              <div class="text-sm text-gray-500">ยอดใช้จ่ายสะสม</div>
              <div class="text-2xl font-bold text-gray-800">{{ formatTHB(analyticsStore.summary?.spent_month || 0) }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-500">จำนวนรายการ</div>
              <div class="text-xl font-semibold text-gray-700">{{ analyticsStore.summary?.total_expenses || 0 }} รายการ</div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <Card>
      <template #title>รายการล่าสุด</template>
      <template #content>
        <div v-if="expensesStore.loading" class="text-center p-4">กำลังโหลด...</div>
        <div v-else-if="!expensesStore.expenses.length" class="text-center p-4 text-gray-500">ยังไม่มีรายการใช้จ่าย</div>
        <div v-else class="flex flex-col gap-3">
          <div v-for="expense in expensesStore.expenses" :key="expense.id" 
               class="flex justify-between items-center p-3 bg-gray-50 rounded-lg border border-gray-100 hover:bg-gray-100 transition-colors cursor-pointer"
               @click="router.push(`/expenses/${expense.id}/edit`)">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                <i class="pi pi-receipt"></i>
              </div>
              <div>
                <div class="font-semibold">{{ expense.menu?.name || 'รายจ่าย' }}</div>
                <div class="text-xs text-gray-500">{{ expense.restaurant?.name || expense.category }} • {{ new Date(expense.date).toLocaleDateString('th-TH') }}</div>
              </div>
            </div>
            <div class="font-bold text-gray-800">
              {{ formatTHB(expense.amount) }}
            </div>
          </div>
        </div>
        <div class="mt-4 text-center">
          <Button label="ดูประวัติทั้งหมด" text @click="router.push('/history')" />
        </div>
      </template>
    </Card>
  </div>
</template>

<style scoped>
:deep(.p-progressbar-danger .p-progressbar-value) {
  background-color: #ef4444;
}
:deep(.p-progressbar-success .p-progressbar-value) {
  background-color: #22c55e;
}
</style>
