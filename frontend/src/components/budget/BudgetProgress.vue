<script setup lang="ts">
import { computed } from 'vue'
import ProgressBar from 'primevue/progressbar'
import { formatTHB } from '@/utils/currency'

interface Props {
  dailyBudget: number
  spentToday: number
}

const props = defineProps<Props>()

const remaining = computed(() => Math.max(0, props.dailyBudget - props.spentToday))
const percentage = computed(() => {
  if (props.dailyBudget <= 0) return 100
  return Math.min(100, Math.round((props.spentToday / props.dailyBudget) * 100))
})

const isOverBudget = computed(() => props.spentToday > props.dailyBudget)
const statusColor = computed(() => {
  if (percentage.value < 50) return '#10B981' // Green
  if (percentage.value < 90) return '#F59E0B' // Yellow/Orange
  return '#EF4444' // Red
})
</script>

<template>
  <div class="budget-progress">
    <div class="budget-header">
      <span class="title">งบประมาณวันนี้</span>
      <span class="spent">{{ formatTHB(spentToday) }} / {{ formatTHB(dailyBudget) }}</span>
    </div>
    
    <ProgressBar :value="percentage" :showValue="false" class="custom-progress" :style="{'--progress-color': statusColor}" />
    
    <div class="budget-footer">
      <span v-if="isOverBudget" class="over-budget">
        <i class="pi pi-exclamation-triangle"></i> เกินงบไป {{ formatTHB(spentToday - dailyBudget) }}
      </span>
      <span v-else class="remaining">
        เหลืออีก {{ formatTHB(remaining) }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.budget-progress {
  background: var(--surface-color);
  padding: 1rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--surface-border);
}

.budget-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.title {
  font-weight: 600;
  color: var(--text-color);
}

.spent {
  color: #666;
  font-size: 0.9rem;
}

.custom-progress {
  height: 0.75rem;
}

.custom-progress :deep(.p-progressbar-value) {
  background-color: var(--progress-color);
}

.budget-footer {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  text-align: right;
}

.over-budget {
  color: #EF4444;
  font-weight: 600;
}

.remaining {
  color: #10B981;
}
</style>
