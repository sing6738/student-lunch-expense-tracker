<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<template>
  <nav v-if="authStore.isAuthenticated" class="mobile-nav-bar" aria-label="แถบนำทางล่าง">
    <div class="nav-content">
      <!-- 1. วันนี้ -->
      <router-link to="/" class="nav-tab" active-class="tab-active" exact>
        <div class="tab-icon-wrap">
          <i class="pi pi-home"></i>
        </div>
        <span class="tab-label">วันนี้</span>
      </router-link>

      <!-- 2. ประวัติ -->
      <router-link to="/history" class="nav-tab" active-class="tab-active">
        <div class="tab-icon-wrap">
          <i class="pi pi-history"></i>
        </div>
        <span class="tab-label">ประวัติ</span>
      </router-link>

      <!-- 3. ปุ่มบันทึก (Center Floating Action Button) -->
      <router-link to="/expenses/add" class="nav-fab" aria-label="บันทึกมื้อกลางวัน">
        <div class="fab-circle">
          <i class="pi pi-plus"></i>
        </div>
        <span class="fab-label">บันทึก</span>
      </router-link>

      <!-- 4. กินอะไรดี? (Roulette) -->
      <router-link to="/what-to-eat" class="nav-tab roulette-tab" active-class="tab-active">
        <div class="tab-icon-wrap">
          <i class="pi pi-sparkles"></i>
        </div>
        <span class="tab-label">กินอะไรดี</span>
      </router-link>

      <!-- 5. สถิติ -->
      <router-link to="/analytics" class="nav-tab" active-class="tab-active">
        <div class="tab-icon-wrap">
          <i class="pi pi-chart-bar"></i>
        </div>
        <span class="tab-label">สถิติ</span>
      </router-link>
    </div>
  </nav>
</template>

<style scoped>
.mobile-nav-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 45;
  background-color: #ffffff;
  border-top: 1px solid var(--surface-border);
  box-shadow: 0 -3px 12px rgba(27, 77, 62, 0.08);
  padding-bottom: max(0.4rem, env(safe-area-inset-bottom, 0px));
}

@media (min-width: 768px) {
  .mobile-nav-bar {
    display: none;
  }
}

.nav-content {
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 56px;
  position: relative;
  max-width: 500px;
  margin: 0 auto;
  padding: 0 0.5rem;
}

.nav-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: var(--text-muted);
  flex: 1;
  height: 100%;
  min-height: 44px;
  transition: all 0.15s ease;
  position: relative;
}

.tab-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 24px;
}

.tab-icon-wrap i {
  font-size: 1.2rem;
  transition: transform 0.15s ease;
}

.tab-label {
  font-size: 0.68rem;
  font-weight: 500;
  margin-top: 2px;
  line-height: 1;
}

.tab-active {
  color: var(--primary-color) !important;
  font-weight: 600;
}

.tab-active .tab-icon-wrap i {
  transform: scale(1.15);
}

.roulette-tab.tab-active {
  color: var(--mango-dark) !important;
}

/* Center FAB */
.nav-fab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  margin-top: -24px;
  flex: 1;
  position: relative;
  min-height: 44px;
}

.fab-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, #2D6A53 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(27, 77, 62, 0.4);
  border: 3px solid #ffffff;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.fab-circle i {
  font-size: 1.35rem;
  font-weight: bold;
}

.nav-fab:active .fab-circle {
  transform: scale(0.92);
}

.fab-label {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--primary-color);
  margin-top: 2px;
}
</style>
