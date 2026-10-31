<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useExpensesStore } from '@/stores/expenses'
import { useBudgetStore } from '@/stores/budget'
import { useFormat } from '@/composables/useFormat'
import ExpenseForm from '@/components/expense/ExpenseForm.vue'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const route = useRoute()
const expensesStore = useExpensesStore()
const budgetStore = useBudgetStore()
const toast = useToast()
const { formatTHB } = useFormat()

// Pre-fill query parameters if navigated from roulette or quick reorder
const initialData = computed(() => {
  return {
    restaurant_id: route.query.restaurant_id ? Number(route.query.restaurant_id) : undefined,
    menu_id: route.query.menu_id ? Number(route.query.menu_id) : undefined,
    price: route.query.price ? Number(route.query.price) : undefined,
    category: route.query.category as string || undefined,
  }
})

// Success state modal/view
const showSuccessModal = ref(false)
const savedRecord = ref<{ amount: number; isOffline: boolean } | null>(null)
const isSubmitting = ref(false)

const handleSubmit = async (data: any) => {
  isSubmitting.value = true
  try {
    const status = await expensesStore.addExpense(data)
    await budgetStore.fetchBudgetSummary()
    
    savedRecord.value = {
      amount: data.amount,
      isOffline: status === 'offline'
    }
    showSuccessModal.value = true

    if (status === 'offline') {
      toast.add({ severity: 'info', summary: 'โหมดออฟไลน์', detail: 'บันทึกรายการลงในเครื่องแล้ว และจะซิงค์ให้อัตโนมัติเมื่อต่อเน็ต', life: 3000 })
    }
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'บันทึกไม่สำเร็จ', detail: expensesStore.error || err.message, life: 3000 })
  } finally {
    isSubmitting.value = false
  }
}

function handleAddAnother() {
  showSuccessModal.value = false
  savedRecord.value = null
  // Replace route to clear queries
  router.replace('/expenses/add')
}

function handleBackHome() {
  router.push('/')
}
</script>

<template>
  <div class="add-expense-page">
    <!-- Success Modal Overlay -->
    <div v-if="showSuccessModal" class="success-overlay" role="dialog" aria-modal="true" aria-labelledby="success-title">
      <div class="success-card">
        <div class="success-icon-wrap">
          <span class="success-emoji">🎉</span>
        </div>
        
        <h2 id="success-title" class="success-title">บันทึกเรียบร้อย!</h2>
        <p class="success-sub">
          {{ savedRecord?.isOffline ? 'บันทึกในเครื่องแล้ว (รอซิงค์เมื่อออนไลน์)' : 'ข้อมูลมื้อเที่ยงถูกบันทึกเข้าระบบแล้ว' }}
        </p>

        <!-- Summary Figures -->
        <div class="success-summary-box">
          <div class="summary-line">
            <span class="label">ยอดที่บันทึก:</span>
            <span class="value font-bold text-main">{{ formatTHB(savedRecord?.amount || 0) }}</span>
          </div>
          <div class="summary-line">
            <span class="label">งบคงเหลือวันนี้:</span>
            <span class="value font-bold" :class="(budgetStore.summary?.remaining_today || 0) < 0 ? 'text-coral' : 'text-primary'">
              {{ formatTHB(budgetStore.summary?.remaining_today || 0) }}
            </span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="success-actions">
          <button type="button" class="action-btn-secondary" @click="handleAddAnother">
            <i class="pi pi-plus"></i>
            เพิ่มอีกรายการ
          </button>
          <button type="button" class="action-btn-primary" @click="handleBackHome">
            <i class="pi pi-home"></i>
            กลับหน้าวันนี้
          </button>
        </div>
      </div>
    </div>

    <!-- Header bar -->
    <div class="page-header">
      <button type="button" class="back-link-btn" @click="router.back()">
        <i class="pi pi-arrow-left"></i>
      </button>
      <div>
        <h1 class="page-title">บันทึกมื้อกลางวัน</h1>
        <p class="page-sub">บันทึกง่าย รวดเร็วในไม่กี่วินาที</p>
      </div>
    </div>

    <!-- Form Container -->
    <div class="form-wrapper">
      <ExpenseForm 
        :key="route.fullPath"
        :initial-data="initialData"
        @submit="handleSubmit" 
        @cancel="router.back()" 
      />
    </div>
  </div>
</template>

<style scoped>
.add-expense-page {
  max-width: 600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.back-link-btn {
  background: #ffffff;
  border: 1px solid var(--surface-border);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-main);
  font-size: 1rem;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
  line-height: 1.2;
}

.page-sub {
  font-size: 0.775rem;
  color: var(--text-muted);
  margin: 0.15rem 0 0;
}

.form-wrapper {
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius-lg);
  padding: 1.25rem 1rem;
  box-shadow: 0 4px 16px rgba(27, 77, 62, 0.05);
}

/* Success Modal */
.success-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.success-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 1.75rem 1.5rem;
  width: 100%;
  max-width: 360px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  animation: popIn 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes popIn {
  from { transform: scale(0.85); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.success-icon-wrap {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #E8F5E9;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
}

.success-emoji {
  font-size: 2rem;
}

.success-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0 0 0.25rem;
}

.success-sub {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin: 0 0 1.25rem;
}

.success-summary-box {
  background: var(--surface-hover);
  border-radius: var(--border-radius);
  padding: 0.85rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.summary-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.text-coral {
  color: var(--warning-coral);
}

.success-actions {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.action-btn-primary {
  width: 100%;
  background: var(--primary-color);
  color: #ffffff;
  border: none;
  border-radius: var(--border-radius);
  padding: 0.75rem;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-family: inherit;
  min-height: 48px;
}

.action-btn-secondary {
  width: 100%;
  background: #ffffff;
  color: var(--text-main);
  border: 1.5px solid var(--surface-border);
  border-radius: var(--border-radius);
  padding: 0.75rem;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-family: inherit;
  min-height: 48px;
}

.action-btn-secondary:hover {
  background: var(--surface-hover);
}
</style>
