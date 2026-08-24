<script setup lang="ts">
import { formatTHB } from '@/utils/currency'
import { formatDateShortTH } from '@/utils/date'
import { EXPENSE_CATEGORIES, CATEGORY_COLORS } from '@/utils/constants'
import type { Expense } from '@/types/expense'

interface Props {
  expense: Expense
  onEdit?: (expense: Expense) => void
  onDelete?: (expense: Expense) => void
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true,
})

const categoryInfo = EXPENSE_CATEGORIES.find(c => c.value === props.expense.category)
const categoryColor = categoryInfo ? CATEGORY_COLORS[props.expense.category] : '#9E9E9E'
</script>

<template>
  <div class="expense-card">
    <div class="expense-header">
      <div class="expense-category" :style="{ backgroundColor: categoryColor + '20', borderColor: categoryColor }">
        <i :class="['pi', categoryInfo?.icon]" :style="{ color: categoryColor }" />
      </div>
      <div class="expense-meta">
        <span class="expense-restaurant">{{ expense.restaurant?.name || 'ร้านไม่ทราบ' }}</span>
        <span class="expense-menu">{{ expense.menu?.name || 'เมนูไม่ทราบ' }}</span>
      </div>
      <div class="expense-amount">{{ formatTHB(expense.amount) }}</div>
    </div>

    <div class="expense-details">
      <div class="expense-date">
        <i class="pi pi-calendar" />
        <span>{{ formatDateShortTH(expense.date) }}</span>
      </div>
      <div v-if="expense.note" class="expense-note">{{ expense.note }}</div>
    </div>

    <div v-if="showActions && (onEdit || onDelete)" class="expense-actions">
      <button v-if="onEdit" class="p-button p-button-text p-button-sm" @click="onEdit(expense)">
        <i class="pi pi-pencil" /> แก้ไข
      </button>
      <button v-if="onDelete" class="p-button p-button-text p-button-sm p-button-danger" @click="onDelete(expense)">
        <i class="pi pi-trash" /> ลบ
      </button>
    </div>
  </div>
</template>

<style scoped>
.expense-card {
  background: var(--surface-color);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  padding: 1rem;
  transition: box-shadow 0.2s, transform 0.2s;
}
.expense-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}
.expense-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}
.expense-category {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid;
}
.expense-meta {
  flex: 1;
}
.expense-restaurant {
  display: block;
  font-weight: 600;
}
.expense-menu {
  display: block;
  font-size: 0.85rem;
  color: #666;
}
.expense-amount {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--primary-color);
}
.expense-details {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.85rem;
  color: #666;
}
.expense-date, .expense-note {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}
.expense-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--surface-border);
}
</style>
