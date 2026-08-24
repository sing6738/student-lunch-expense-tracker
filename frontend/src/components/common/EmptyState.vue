<script setup lang="ts">
interface Props {
  icon?: string
  title: string
  message?: string
  actionLabel?: string
  actionIcon?: string
  onAction?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  icon: 'pi pi-inbox',
})
</script>

<template>
  <div class="empty-state">
    <i :class="['empty-icon', icon]" />
    <h3 class="empty-title">{{ title }}</h3>
    <p v-if="message" class="empty-message">{{ message }}</p>
    <button
      v-if="actionLabel && onAction"
      class="p-button p-button-outlined empty-action"
      @click="onAction"
    >
      <i :class="actionIcon" v-if="actionIcon" />
      {{ actionLabel }}
    </button>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  text-align: center;
  color: #888;
}

.empty-icon {
  font-size: 4rem;
  color: #ccc;
  margin-bottom: 1rem;
}

.empty-title {
  margin: 0 0 0.5rem;
  color: #555;
  font-size: 1.125rem;
}

.empty-message {
  margin: 0 0 1.5rem;
  font-size: 0.9rem;
  max-width: 300px;
}

.empty-action {
  gap: 0.5rem;
}
</style>
