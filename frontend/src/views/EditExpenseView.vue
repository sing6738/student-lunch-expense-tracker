<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useExpensesStore } from '@/stores/expenses'
import { expensesApi } from '@/api/expenses'
import ExpenseForm from '@/components/expense/ExpenseForm.vue'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const route = useRoute()
const expensesStore = useExpensesStore()
const toast = useToast()

const expenseId = Number(route.params.id)
const expenseData = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await expensesApi.get(expenseId)
    if (res.data.success && res.data.data) {
      expenseData.value = res.data.data
    }
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'โหลดข้อมูลไม่สำเร็จ', detail: err.message, life: 3000 })
  } finally {
    loading.value = false
  }
})

const handleSubmit = async (data: any) => {
  try {
    await expensesStore.updateExpense(expenseId, data)
    toast.add({ severity: 'success', summary: 'สำเร็จ', detail: 'แก้ไขข้อมูลมื้ออาหารแล้ว', life: 3000 })
    router.push('/history')
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'เกิดข้อผิดพลาด', detail: expensesStore.error || err.message, life: 3000 })
  }
}
</script>

<template>
  <div class="edit-expense-page">
    <div class="page-header">
      <button type="button" class="back-link-btn" @click="router.back()">
        <i class="pi pi-arrow-left"></i>
      </button>
      <div>
        <h1 class="page-title">แก้ไขรายการรายจ่าย</h1>
        <p class="page-sub">ปรับปรุงข้อมูลเมนูหรือยอดเงิน</p>
      </div>
    </div>

    <div v-if="loading" class="text-center p-8 text-muted">
      <i class="pi pi-spin pi-spinner text-2xl"></i>
      <p class="mt-2">กำลังโหลดข้อมูลรายการ...</p>
    </div>

    <div v-else-if="expenseData" class="form-wrapper">
      <ExpenseForm 
        :initial-data="expenseData"
        :is-editing="true"
        @submit="handleSubmit"
        @cancel="router.back()"
      />
    </div>
  </div>
</template>

<style scoped>
.edit-expense-page {
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
</style>
