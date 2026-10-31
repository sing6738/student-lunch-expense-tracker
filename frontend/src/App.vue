<script setup lang="ts">
import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import AppHeader from '@/components/common/AppHeader.vue'
import AppFooter from '@/components/common/AppFooter.vue'
import MobileNavBar from '@/components/common/MobileNavBar.vue'
</script>

<template>
  <div class="app-container">
    <AppHeader />
    
    <main class="main-content">
      <RouterView />
    </main>

    <AppFooter />
    <MobileNavBar />
    
    <!-- Global UI Components -->
    <Toast />
    <ConfirmDialog />
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
  background-color: var(--surface-ground);
}

.main-content {
  flex: 1;
  padding: 0.75rem;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
  /* Ensure padding on mobile so content isn't covered by bottom nav */
  padding-bottom: calc(70px + env(safe-area-inset-bottom, 1rem));
}

@media (min-width: 768px) {
  .main-content {
    padding: 1.5rem 1rem;
    padding-bottom: 2rem;
  }
}
</style>
