<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useExpensesStore } from '../stores/expenses'
import { useFormat } from '../composables/useFormat'
import ExpenseList from '../components/expense/ExpenseList.vue' // Assuming this exists or we can use PrimeVue DataTable directly
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'

const router = useRouter()
const { formatTHB } = useFormat()
const expensesStore = useExpensesStore()
const page = ref(1)

onMounted(async () => {
  await loadData()
})

const loadData = async () => {
  await expensesStore.fetchExpenses({ page: page.value, per_page: 20 })
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('th-TH', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>

<template>
  <div class="p-4 max-w-6xl mx-auto">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">ประวัติการใช้จ่าย</h1>
      <Button icon="pi pi-download" label="ส่งออก CSV" @click="expensesStore.exportCsv()" class="p-button-outlined" />
    </div>
    
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <DataTable :value="expensesStore.expenses" :loading="expensesStore.loading" paginator :rows="10" 
                 :rowsPerPageOptions="[10, 20, 50]" responsiveLayout="scroll"
                 emptyMessage="ไม่พบข้อมูล">
        <Column field="date" header="วันที่" sortable>
          <template #body="slotProps">
            {{ formatDate(slotProps.data.date) }}
          </template>
        </Column>
        <Column field="menu.name" header="รายการ">
          <template #body="slotProps">
            <span class="font-medium">{{ slotProps.data.menu?.name || 'ไม่มีชื่อเมนู' }}</span>
          </template>
        </Column>
        <Column field="restaurant.name" header="ร้านอาหาร">
          <template #body="slotProps">
            <span class="text-gray-600">{{ slotProps.data.restaurant?.name || '-' }}</span>
          </template>
        </Column>
        <Column field="category" header="หมวดหมู่"></Column>
        <Column field="amount" header="จำนวนเงิน" sortable alignFrozen="right">
          <template #body="slotProps">
            <span class="font-bold text-gray-800">{{ formatTHB(slotProps.data.amount) }}</span>
          </template>
        </Column>
        <Column header="จัดการ" :exportable="false" style="min-width: 8rem">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" class="p-button-rounded p-button-text" 
                    @click="router.push(`/expenses/${slotProps.data.id}/edit`)" />
            <Button icon="pi pi-trash" class="p-button-rounded p-button-text p-button-danger" 
                    @click="expensesStore.deleteExpense(slotProps.data.id)" />
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>
