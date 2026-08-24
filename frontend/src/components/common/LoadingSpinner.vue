<script setup lang="ts">
import ProgressSpinner from 'primevue/progressspinner'

interface Props {
  size?: number;
}

const props = withDefaults(defineProps<Props>(), {
  size: 50
})
</script>

<template>
  <div class="loading-container">
    <ProgressSpinner :style="{ width: size + 'px', height: size + 'px' }" strokeWidth="4" />
  </div>
</template>

<style scoped>
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}
</style>
