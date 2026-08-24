<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import { formatTHB } from '@/utils/currency'
import { formatDateShortTH } from '@/utils/date'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

interface Props {
  labels: string[]
  data: number[]
}

const props = defineProps<Props>()

const chartData = computed(() => ({
  labels: props.labels.map(d => formatDateShortTH(d)),
  datasets: [
    {
      label: 'รายจ่าย (บาท)',
      backgroundColor: '#2E7D32',
      borderColor: '#2E7D32',
      data: props.data,
      tension: 0.3
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: (value: any) => '฿' + value
      }
    }
  },
  plugins: {
    tooltip: {
      callbacks: {
        label: (context: any) => formatTHB(context.raw)
      }
    }
  }
}
</script>

<template>
  <div class="chart-container">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}
</style>
