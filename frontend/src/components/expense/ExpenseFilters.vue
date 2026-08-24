<script setup lang="ts">
import { useField } from 'vee-validate'
import { useRestaurantsStore } from '@/stores/restaurants'
import { EXPENSE_CATEGORIES } from '@/utils/constants'
import type { ExpenseCategory, ExpenseFilters } from '@/types/expense'
import DatePicker from 'primevue/datepicker'
import Select from 'primevue/select'

interface Props {
  modelValue: ExpenseFilters
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [filters: ExpenseFilters]
  search: [filters: ExpenseFilters]
  reset: []
}>()

const restaurantsStore = useRestaurantsStore()

const { value: dateFrom } = useField<string>('date_from')
const { value: dateTo } = useField<string>('date_to')
const { value: category } = useField<ExpenseCategory>('category')
const { value: restaurantId } = useField<number>('restaurant_id')

function handleSearch(): void {
  const filters: ExpenseFilters = {
    date_from: dateFrom.value || undefined,
    date_to: dateTo.value || undefined,
    category: category.value || undefined,
    restaurant_id: restaurantId.value || undefined,
    page: 1,
  }
  emit('update:modelValue', filters)
  emit('search', filters)
}

function handleReset(): void {
  dateFrom.value = ''
  dateTo.value = ''
  category.value = undefined
  restaurantId.value = undefined
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
        <label>จากวันที่</label>
        <DatePicker v-model="dateFrom" dateFormat="yy-mm-dd" class="p-fluid" />
      </div>

      <div class="filter-group">
        <label>ถึงวันที่</label>
        <DatePicker v-model="dateTo" dateFormat="yy-mm-dd" class="p-fluid" />
      </div>

      <div class="filter-group">
        <label>หมวดหมู่</label>
        <Select v-model="category" :options="EXPENSE_CATEGORIES" optionLabel="label" optionValue="value" placeholder="ทั้งหมด" class="p-fluid" />
      </div>

      <div class="filter-group">
        <label>ร้านอาหาร</label>
        <Select v-model="restaurantId" :options="restaurantsStore.activeRestaurants" optionLabel="name" optionValue="id" placeholder="ทั้งหมด" class="p-fluid" />
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
