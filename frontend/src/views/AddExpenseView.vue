<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useExpensesStore } from '../stores/expenses'
import ExpenseForm from '../components/expense/ExpenseForm.vue'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const expensesStore = useExpensesStore()
const toast = useToast()

const handleSubmit = async (data: any) => {
  try {
    const status = await expensesStore.addExpense(data)
    if (status === 'offline') {
      toast.add({ severity: 'info', summary: 'ออฟไลน์', detail: 'บันทึกรายการลงคิวออฟไลน์แล้ว', life: 3000 })
    } else {
      toast.add({ severity: 'success', summary: 'สำเร็จ', detail: 'เพิ่มรายจ่ายเรียบร้อยแล้ว', life: 3000 })
    }
    router.push('/')
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'ข้อผิดพลาด', detail: expensesStore.error || err.message, life: 3000 })
  }
}
</script>

<template>
  <div class="p-4 max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">เพิ่มรายจ่ายใหม่</h1>
    <div class="bg-white p-4 md:p-6 rounded-xl shadow-sm border border-gray-100">
      <ExpenseForm @submit="handleSubmit" @cancel="router.back()" />
    </div>
  </div>
</template>
