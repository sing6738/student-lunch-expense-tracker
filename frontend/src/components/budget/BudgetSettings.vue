<script setup lang="ts">
import { ref } from 'vue'
import { useBudgetStore } from '@/stores/budget'
import InputNumber from 'primevue/inputnumber'
import { useToast } from 'primevue/usetoast'

const budgetStore = useBudgetStore()
const toast = useToast()

const dailyBudget = ref(budgetStore.summary?.daily_budget || 0)
const loading = ref(false)

async function saveBudget() {
  loading.value = true
  try {
    // TODO: Call API to update budget
    // await budgetStore.updateBudget(dailyBudget.value)
    toast.add({ severity: 'success', summary: 'สำเร็จ', detail: 'อัปเดตงบประมาณเรียบร้อย', life: 3000 })
  } catch (err) {
    toast.add({ severity: 'error', summary: 'ข้อผิดพลาด', detail: 'ไม่สามารถอัปเดตงบประมาณได้', life: 3000 })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="budget-settings">
    <h3>ตั้งค่างบประมาณ</h3>
    <div class="field">
      <label>งบประมาณรายวัน (บาท)</label>
      <InputNumber v-model="dailyBudget" :min="0" :step="10" class="p-fluid" />
    </div>
    <button class="p-button p-button-primary" @click="saveBudget" :disabled="loading">
      บันทึกการตั้งค่า
    </button>
  </div>
</template>

<style scoped>
.budget-settings {
  background: var(--surface-color);
  padding: 1.5rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--surface-border);
}
.field {
  margin-bottom: 1rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}
</style>
