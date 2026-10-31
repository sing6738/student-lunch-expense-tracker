<script setup lang="ts">
import { ref } from 'vue'
import { useRestaurantsStore } from '@/stores/restaurants'
import { EXPENSE_CATEGORIES } from '@/utils/constants'
import type { ExpenseCategory, ExpenseFilters } from '@/types/expense'
import DatePicker from 'primevue/datepicker'
import Select from 'primevue/select'
import { formatDateInput } from '@/utils/date'

interface Props {
  modelValue: ExpenseFilters
}

defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [filters: ExpenseFilters]
  search: [filters: ExpenseFilters]
  reset: []
}>()

const restaurantsStore = useRestaurantsStore()

const dateFrom = ref<Date | null>(null)
const dateTo = ref<Date | null>(null)
const category = ref<ExpenseCategory | null>(null)
const restaurantId = ref<number | null>(null)

function handleSearch(): void {
  const filters: ExpenseFilters = {
    date_from: dateFrom.value ? formatDateInput(dateFrom.value) : undefined,
    date_to: dateTo.value ? formatDateInput(dateTo.value) : undefined,
    category: category.value || undefined,
    restaurant_id: restaurantId.value || undefined,
    page: 1,
  }
  emit('update:modelValue', filters)
  emit('search', filters)
}

function handleReset(): void {
  dateFrom.value = null
  dateTo.value = null
  category.value = null
  restaurantId.value = null
  emit('update:modelValue', { page: 1 })
  emit('reset')
}

function hasActiveFilters(): boolean {
  return !!(dateFrom.value || dateTo.value || category.value || restaurantId.value)
}
</script>

<template>
  <div class="expense-filters">
    <div class="filters-row">
      <div class="filter-group">
        <label class="text-xs font-medium text-stone-600">จากวันที่</label>
        <DatePicker v-model="dateFrom" dateFormat="yy-mm-dd" class="w-full" placeholder="เลือกวันที่เริ่มต้น" />
      </div>

      <div class="filter-group">
        <label class="text-xs font-medium text-stone-600">ถึงวันที่</label>
        <DatePicker v-model="dateTo" dateFormat="yy-mm-dd" class="w-full" placeholder="เลือกวันที่สิ้นสุด" />
      </div>

      <div class="filter-group">
        <label class="text-xs font-medium text-stone-600">หมวดหมู่</label>
        <Select v-model="category" :options="EXPENSE_CATEGORIES" optionLabel="label" optionValue="value" placeholder="ทุกหมวดหมู่" class="w-full" showClear />
      </div>

      <div class="filter-group">
        <label class="text-xs font-medium text-stone-600">ร้านอาหาร</label>
        <Select v-model="restaurantId" :options="restaurantsStore.activeRestaurants" optionLabel="name" optionValue="id" placeholder="ทุกร้าน" class="w-full" showClear />
      </div>
    </div>

    <div class="filters-actions">
      <button class="p-button p-button-outlined" @click="handleSearch">กรอง</button>
      <button v-if="hasActiveFilters()" class="p-button p-button-text" @click="handleReset">ล้างตัวกรอง</button>
    </div>
  </div>
</template>

<style scoped>
.expense-filters {
  background: var(--surface-color);
  padding: 1rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--surface-border);
}
.filters-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; }
.filter-group { display: flex; flex-direction: column; gap: 0.25rem; }
.filters-actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem; }
</style>
