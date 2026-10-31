<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useExpensesStore } from '@/stores/expenses'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const expensesStore = useExpensesStore()
const router = useRouter()

const isOnline = ref(navigator.onLine)
const showMoreMenu = ref(false)

function updateOnlineStatus() {
  isOnline.value = navigator.onLine
  if (isOnline.value) {
    expensesStore.syncQueue()
  }
}

onMounted(() => {
  window.addEventListener('online', updateOnlineStatus)
  window.addEventListener('offline', updateOnlineStatus)
  expensesStore.refreshOfflineQueueCount()
})

onUnmounted(() => {
  window.removeEventListener('online', updateOnlineStatus)
  window.removeEventListener('offline', updateOnlineStatus)
})

function logout() {
  showMoreMenu.value = false
  authStore.logout()
  router.push('/login')
}

function handleSync() {
  expensesStore.syncQueue()
}
</script>

<template>
  <header class="app-header">
    <div class="header-container">
      <router-link to="/" class="logo-link">
        <div class="logo-icon">🍱</div>
        <div class="logo-text">
          <span class="logo-title">LunchTrack</span>
          <span class="logo-tagline">เพื่อนคู่ใจมื้อเที่ยง</span>
        </div>
      </router-link>

      <div class="header-right">
        <!-- Offline / Sync Status Badge -->
        <div v-if="!isOnline" class="offline-badge" title="ออฟไลน์อยู่ ข้อมูลจะบันทึกในเครื่อง">
          <span class="offline-dot"></span>
          <span class="offline-text">ออฟไลน์</span>
        </div>
        <div v-else-if="expensesStore.offlineQueueCount > 0" class="sync-badge" @click="handleSync" title="แตะเพื่อซิงค์ข้อมูล">
          <i class="pi pi-sync pi-spin"></i>
          <span>รอซิงค์ ({{ expensesStore.offlineQueueCount }})</span>
        </div>

        <!-- Desktop Navigation -->
        <nav v-if="authStore.isAuthenticated" class="desktop-nav">
          <router-link to="/" class="nav-item">วันนี้</router-link>
          <router-link to="/expenses/add" class="nav-item">บันทึก</router-link>
          <router-link to="/what-to-eat" class="nav-item highlight-nav">
            <i class="pi pi-sparkles"></i>
            กินอะไรดี?
          </router-link>
          <router-link to="/history" class="nav-item">ประวัติ</router-link>
          <router-link to="/analytics" class="nav-item">สถิติ</router-link>
          
          <!-- More dropdown trigger -->
          <div class="more-menu-wrapper">
            <button 
              type="button" 
              class="more-trigger-btn"
              @click="showMoreMenu = !showMoreMenu"
              aria-label="เมนูเพิ่มเติม"
            >
              <span>เมนูอื่น</span>
              <i class="pi pi-angle-down"></i>
            </button>

            <!-- Dropdown popover -->
            <div v-if="showMoreMenu" class="dropdown-menu" @click="showMoreMenu = false">
              <router-link to="/budget" class="dropdown-item">
                <i class="pi pi-wallet"></i>
                ตั้งงบรายวัน
              </router-link>
              <router-link to="/monthly-budget" class="dropdown-item">
                <i class="pi pi-calendar"></i>
                งบประมาณรายเดือน
              </router-link>
              <router-link to="/manage-menus" class="dropdown-item">
                <i class="pi pi-list"></i>
                จัดการร้านและเมนู
              </router-link>
              <router-link to="/orders" class="dropdown-item">
                <i class="pi pi-shopping-bag"></i>
                สั่งอาหารออนไลน์
              </router-link>
              <router-link to="/profile" class="dropdown-item">
                <i class="pi pi-user"></i>
                โปรไฟล์นักเรียน
              </router-link>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item text-danger" @click="logout">
                <i class="pi pi-sign-out"></i>
                ออกจากระบบ
              </button>
            </div>
          </div>
        </nav>

        <!-- Mobile quick menu toggle -->
        <div v-if="authStore.isAuthenticated" class="mobile-more-wrapper">
          <button 
            type="button" 
            class="mobile-more-btn" 
            @click="showMoreMenu = !showMoreMenu"
            aria-label="เมนูทั้งหมด"
          >
            <i class="pi pi-bars"></i>
          </button>
          
          <div v-if="showMoreMenu" class="mobile-dropdown-sheet" @click="showMoreMenu = false">
            <div class="mobile-sheet-content" @click.stop>
              <div class="sheet-header">
                <span class="sheet-title">เมนูเพิ่มเติม</span>
                <button type="button" class="sheet-close-btn" @click="showMoreMenu = false">✕</button>
              </div>
              <div class="sheet-links">
                <router-link to="/budget" class="sheet-link" @click="showMoreMenu = false">
                  <i class="pi pi-wallet"></i>
                  <span>ตั้งค่างบประมาณรายวัน</span>
                </router-link>
                <router-link to="/monthly-budget" class="sheet-link" @click="showMoreMenu = false">
                  <i class="pi pi-calendar"></i>
                  <span>งบประมาณรายเดือน</span>
                </router-link>
                <router-link to="/manage-menus" class="sheet-link" @click="showMoreMenu = false">
                  <i class="pi pi-list"></i>
                  <span>จัดการร้านและเมนูอาหาร</span>
                </router-link>
                <router-link to="/orders" class="sheet-link" @click="showMoreMenu = false">
                  <i class="pi pi-shopping-bag"></i>
                  <span>รายการสั่งซื้อออนไลน์</span>
                </router-link>
                <router-link to="/profile" class="sheet-link" @click="showMoreMenu = false">
                  <i class="pi pi-user"></i>
                  <span>โปรไฟล์และข้อมูลส่วนตัว</span>
                </router-link>
                <div class="sheet-divider"></div>
                <button class="sheet-link sheet-danger" @click="logout">
                  <i class="pi pi-sign-out"></i>
                  <span>ออกจากระบบ</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 40;
  background-color: var(--primary-color);
  color: #ffffff;
  padding: 0.6rem 1rem;
  padding-top: max(0.6rem, env(safe-area-inset-top, 0px));
  box-shadow: 0 2px 8px rgba(27, 77, 62, 0.15);
}

.header-container {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 44px;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  text-decoration: none;
  color: #ffffff;
}

.logo-icon {
  font-size: 1.5rem;
  line-height: 1;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-family: 'Prompt', sans-serif;
  font-weight: 700;
  font-size: 1.15rem;
  letter-spacing: -0.01em;
  color: #ffffff;
  line-height: 1.2;
}

.logo-tagline {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.offline-badge {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background-color: rgba(220, 38, 38, 0.2);
  border: 1px solid rgba(220, 38, 38, 0.4);
  color: #fecaca;
  padding: 0.25rem 0.6rem;
  border-radius: var(--border-radius-full);
  font-size: 0.75rem;
  font-weight: 500;
}

.offline-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #ef4444;
}

.sync-badge {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background-color: rgba(229, 169, 60, 0.25);
  border: 1px solid rgba(229, 169, 60, 0.5);
  color: #fef3c7;
  padding: 0.25rem 0.6rem;
  border-radius: var(--border-radius-full);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
}

.desktop-nav {
  display: none;
  align-items: center;
  gap: 0.5rem;
}

@media (min-width: 768px) {
  .desktop-nav {
    display: flex;
  }
  .mobile-more-wrapper {
    display: none;
  }
}

.nav-item {
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  padding: 0.4rem 0.8rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  min-height: 40px;
}

.nav-item:hover {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.12);
}

.nav-item.router-link-exact-active,
.nav-item.router-link-active {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.18);
  font-weight: 600;
}

.highlight-nav {
  color: var(--mango-accent) !important;
  font-weight: 600;
}

.more-menu-wrapper {
  position: relative;
}

.more-trigger-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  padding: 0.4rem 0.8rem;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  font-family: inherit;
  min-height: 40px;
}

.more-trigger-btn:hover {
  background-color: rgba(255, 255, 255, 0.12);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.4rem);
  right: 0;
  background: #ffffff;
  color: var(--text-main);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--surface-border);
  min-width: 200px;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  z-index: 50;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.8rem;
  color: var(--text-main);
  text-decoration: none;
  font-size: 0.875rem;
  border-radius: var(--border-radius-sm);
  border: none;
  background: transparent;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-family: inherit;
  min-height: 40px;
}

.dropdown-item:hover {
  background-color: var(--surface-hover);
  color: var(--primary-color);
}

.dropdown-divider {
  height: 1px;
  background-color: var(--surface-border);
  margin: 0.4rem 0;
}

.text-danger {
  color: var(--warning-coral) !important;
}

/* Mobile more sheet */
.mobile-more-btn {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 1.25rem;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: var(--border-radius-sm);
}

.mobile-dropdown-sheet {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 100;
  display: flex;
  align-items: flex-end;
}

.mobile-sheet-content {
  background: #ffffff;
  width: 100%;
  border-radius: 20px 20px 0 0;
  padding: 1.25rem;
  padding-bottom: max(1.5rem, env(safe-area-inset-bottom, 1.5rem));
  box-shadow: 0 -4px 20px rgba(0,0,0,0.15);
  animation: slideUp 0.25s ease-out;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.sheet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.sheet-title {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--primary-color);
}

.sheet-close-btn {
  background: #f1f5f9;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  color: #64748b;
}

.sheet-links {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.sheet-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: var(--border-radius-sm);
  color: var(--text-main);
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  background: transparent;
  border: none;
  width: 100%;
  min-height: 44px;
}

.sheet-link:hover, .sheet-link:active {
  background: var(--surface-hover);
}

.sheet-link i {
  font-size: 1.1rem;
  color: var(--primary-color);
}

.sheet-divider {
  height: 1px;
  background: var(--surface-border);
  margin: 0.5rem 0;
}

.sheet-danger {
  color: var(--warning-coral);
}
.sheet-danger i {
  color: var(--warning-coral);
}
</style>
