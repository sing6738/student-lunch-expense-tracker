<script setup lang="ts">
import ExpenseCard from './ExpenseCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import type { Expense } from '@/types/expense'

interface Props {
  expenses: Expense[]
  loading?: boolean
  emptyTitle?: string
  emptyMessage?: string
  onEdit?: (expense: Expense) => void
  onDelete?: (expense: Expense) => void
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  emptyTitle: 'ยังไม่มีรายจ่าย',
  emptyMessage: 'เริ่มบันทึกรายจ่ายวันนี้ได้เลย',
  showActions: true,
})
</script>

<template>
  <div class="expense-list">
    <LoadingSpinner v-if="loading" size="32px" />

    <div v-else-if="expenses.length === 0" class="empty-container">
      <EmptyState
        :title="emptyTitle"
        :message="emptyMessage"
        action-label="เพิ่มรายจ่ายแรก"
        action-icon="pi pi-plus"
        @action="$emit('add-new')"
      />
    </div>

    <div v-else class="expense-cards">
      <ExpenseCard
        v-for="expense in expenses"
        :key="expense.id"
        :expense="expense"
        :show-actions="showActions"
        @edit="onEdit"
        @delete="onDelete"
      />
    </div>
  </div>
</template>

<style scoped>
.expense-list {
  width: 100%;
}
.expense-cards {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.empty-container {
  padding: 2rem 0;
}
</style>
