<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

function logout() {
  authStore.clearAuth()
  router.push('/login')
}
</script>

<template>
  <header class="app-header">
    <div class="logo">
      <i class="pi pi-receipt" style="font-size: 1.5rem"></i>
      <span>LunchTrack</span>
    </div>
    <nav v-if="authStore.isAuthenticated()" class="main-nav">
      <router-link to="/">แดชบอร์ด</router-link>
      <router-link to="/history">ประวัติ</router-link>
      <router-link to="/analytics">สถิติ</router-link>
      <router-link to="/budget">งบประมาณ</router-link>
      <button class="p-button p-button-text p-button-sm p-button-danger logout-btn" @click="logout">
        <i class="pi pi-sign-out"></i>
      </button>
    </nav>
  </header>
</template>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: var(--primary-color);
  color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
}

.main-nav {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.main-nav a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
}

.main-nav a.router-link-active {
  color: white;
  font-weight: 700;
}

.logout-btn {
  color: #ffcdd2;
}
.logout-btn:hover {
  background-color: rgba(255,255,255,0.1);
  color: white;
}
</style>
