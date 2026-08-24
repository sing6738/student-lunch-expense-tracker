<script setup lang="ts">
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { EXPENSE_CATEGORIES, CATEGORY_COLORS } from '@/utils/constants'
import { formatTHB } from '@/utils/currency'

ChartJS.register(ArcElement, Tooltip, Legend)

interface CategoryData {
  category: string
  amount: number
}

interface Props {
  data: CategoryData[]
}

const props = defineProps<Props>()

const chartData = computed(() => {
  const labels = props.data.map(d => {
    const cat = EXPENSE_CATEGORIES.find(c => c.value === d.category)
    return cat ? cat.label : 'อื่นๆ'
  })
  
  const colors = props.data.map(d => CATEGORY_COLORS[d.category] || CATEGORY_COLORS['other'])
  
  return {
    labels,
    datasets: [
      {
        backgroundColor: colors,
        data: props.data.map(d => d.amount)
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    tooltip: {
      callbacks: {
        label: (context: any) => ` ${context.label}: ${formatTHB(context.raw)}`
      }
    }
  }
}
</script>

<template>
  <div class="chart-container">
    <Doughnut :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}
</style>
