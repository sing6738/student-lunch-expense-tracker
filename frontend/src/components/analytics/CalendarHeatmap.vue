<script setup lang="ts">
// Simple mock for Calendar Heatmap until actual implementation
interface Props {
  data: any[]
}
const props = defineProps<Props>()
</script>

<template>
  <div class="calendar-heatmap">
    <div class="placeholder">
      <i class="pi pi-calendar"></i>
      <p>แผนผังปฏิทินรายจ่าย (กำลังพัฒนา)</p>
    </div>
  </div>
</template>

<style scoped>
.calendar-heatmap {
  background: var(--surface-color);
  padding: 2rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--surface-border);
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}
.placeholder {
  text-align: center;
  color: #888;
}
.placeholder i {
  font-size: 2rem;
  margin-bottom: 1rem;
}
</style>
