<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRestaurantsStore } from '@/stores/restaurants'
import { useBudgetStore } from '@/stores/budget'
import { useExpensesStore } from '@/stores/expenses'
import { useFormat } from '@/composables/useFormat'
import type { Menu } from '@/types/restaurant'
import Button from 'primevue/button'

const router = useRouter()
const { formatTHB } = useFormat()
const restaurantsStore = useRestaurantsStore()
const budgetStore = useBudgetStore()
const expensesStore = useExpensesStore()

interface EnrichedMenu extends Menu {
  restaurantName: string;
}

// Loading & error state
const loading = ref(true)
const loadError = ref<string | null>(null)
const allMenus = ref<EnrichedMenu[]>([])

// Filter preferences (persisted locally)
const STORAGE_KEY = 'lunch_roulette_prefs'
const savedPrefs = (() => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
})()

const selectedRestaurantId = ref<number | null>(savedPrefs?.restaurantId ?? null)
const excludeRecent = ref<boolean>(savedPrefs?.excludeRecent ?? true)
const budgetCeiling = ref<number>(savedPrefs?.budgetCeiling ?? 60)
const budgetMode = ref<'custom' | 'unlimited'>(savedPrefs?.budgetMode ?? 'custom')

// Roulette state
const isSpinning = ref(false)
const selectedResult = ref<EnrichedMenu | null>(null)
const tickerMenu = ref<EnrichedMenu | null>(null)
const showAllMatchingModal = ref(false)

function savePrefs() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      restaurantId: selectedRestaurantId.value,
      excludeRecent: excludeRecent.value,
      budgetCeiling: budgetCeiling.value,
      budgetMode: budgetMode.value
    }))
  } catch {
    // Ignore storage errors
  }
}

// Load data
async function loadRouletteData() {
  loading.value = true
  loadError.value = null
  try {
    const results = await Promise.allSettled([
      restaurantsStore.fetchRestaurants(),
      budgetStore.fetchBudgetSummary(),
      expensesStore.fetchExpenses({ per_page: 15 })
    ])

    // If fetching restaurants failed, do NOT treat this as "no menus"!
    if (results[0].status === 'rejected') {
      loadError.value = 'ไม่สามารถเชื่อมต่อรายชื่อร้านค้าได้ กรุณาตรวจสอบสัญญาณเน็ตแล้วลองใหม่'
      return
    }

    const activeRestaurants = restaurantsStore.activeRestaurants
    if (activeRestaurants.length === 0) {
      allMenus.value = []
      return
    }

    const menuPromises = activeRestaurants.map(async (r) => {
      const list = await restaurantsStore.fetchMenus(r.id)
      return list.map(m => ({
        ...m,
        restaurantName: r.name
      }))
    })

    const menuResults = await Promise.allSettled(menuPromises)
    const fulfilledMenus = menuResults
      .filter((r): r is PromiseFulfilledResult<EnrichedMenu[]> => r.status === 'fulfilled')
      .flatMap(r => r.value)

    // If all menu fetches failed, it's a network error, not genuine empty state
    if (fulfilledMenus.length === 0 && menuResults.some(r => r.status === 'rejected')) {
      loadError.value = 'เกิดข้อผิดพลาดในการโหลดรายการเมนูอาหาร กรุณาลองใหม่อีกครั้ง'
      return
    }

    allMenus.value = fulfilledMenus.filter(m => m.is_active && m.price > 0)

    // Default budget ceiling to remaining daily budget if available and positive
    const remaining = budgetStore.summary?.remaining_today
    if (remaining !== undefined && remaining > 0 && !savedPrefs?.budgetCeiling) {
      budgetCeiling.value = remaining
    }
  } catch (err: any) {
    loadError.value = err.message || 'ไม่สามารถโหลดข้อมูลเมนูอาหารได้'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRouletteData()
})

// Recent menu IDs to exclude
const recentMenuIds = computed(() => {
  const ids = new Set<number>()
  for (const exp of expensesStore.expenses) {
    if (exp.menu_id) ids.add(exp.menu_id)
  }
  return ids
})

// Frequent restaurant/menus map for recommendations
const frequentMenuIds = computed(() => {
  const counts = new Map<number, number>()
  for (const exp of expensesStore.expenses) {
    if (exp.menu_id) {
      counts.set(exp.menu_id, (counts.get(exp.menu_id) || 0) + 1)
    }
  }
  return counts
})

// Eligible menus matching filters
const eligibleMenus = computed(() => {
  return allMenus.value.filter(menu => {
    // Restaurant filter
    if (selectedRestaurantId.value !== null && menu.restaurant_id !== selectedRestaurantId.value) {
      return false
    }

    // Budget ceiling
    if (budgetMode.value === 'custom' && menu.price > budgetCeiling.value) {
      return false
    }

    // Exclude recent
    if (excludeRecent.value && recentMenuIds.value.has(menu.id)) {
      return false
    }

    return true
  })
})

// Recommendation reason
const recommendationReason = computed(() => {
  if (!selectedResult.value) return ''
  const remaining = budgetStore.summary?.remaining_today || 0
  const freq = frequentMenuIds.value.get(selectedResult.value.id) || 0

  if (freq >= 2) {
    return '🌟 เมนูโปรดที่คุณเลือกสั่งบ่อย'
  }
  if (remaining > 0 && selectedResult.value.price <= remaining) {
    return '✨ อร่อยสบายใจ อยู่ในงบที่เหลือวันนี้'
  }
  if (selectedResult.value.price <= 50) {
    return '👍 เมนูประหยัด คุ้มค่าช่วงพักเที่ยง'
  }
  return '🎯 สุ่มได้จากร้านโรงอาหารที่คุณบันทึกไว้'
})

// Budget fit status
const budgetFitStatus = computed(() => {
  if (!selectedResult.value) return { fits: true, label: '', textClass: '' }
  const remaining = budgetStore.summary?.remaining_today || 0
  const daily = budgetStore.summary?.daily_budget || 0

  if (daily <= 0) {
    return {
      fits: true,
      label: 'ยังไม่ได้ตั้งงบรายวัน',
      textClass: 'text-muted'
    }
  }

  if (selectedResult.value.price <= remaining) {
    const leftAfter = remaining - selectedResult.value.price
    return {
      fits: true,
      label: `อยู่ในงบวันนี้ (กินแล้วยังเหลือ ${formatTHB(leftAfter)})`,
      textClass: 'text-good'
    }
  } else {
    const over = selectedResult.value.price - remaining
    return {
      fits: false,
      label: `เกินงบคงเหลือ ${formatTHB(over)} (เลือกได้ถ้ามื้อนี้จำเป็น)`,
      textClass: 'text-warning'
    }
  }
})

// Check prefers-reduced-motion
const prefersReducedMotion = () => {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

// Random draw interaction
function spinRoulette() {
  if (eligibleMenus.value.length === 0 || isSpinning.value) return
  savePrefs()

  const pool = eligibleMenus.value
  
  if (prefersReducedMotion() || pool.length === 1) {
    const winner = pool[Math.floor(Math.random() * pool.length)]
    selectedResult.value = winner
    return
  }

  isSpinning.value = true
  selectedResult.value = null

  let step = 0
  const totalSteps = 16
  const interval = 80

  const timer = setInterval(() => {
    step++
    const randomIndex = Math.floor(Math.random() * pool.length)
    tickerMenu.value = pool[randomIndex]

    if (step >= totalSteps) {
      clearInterval(timer)
      isSpinning.value = false
      selectedResult.value = pool[Math.floor(Math.random() * pool.length)]
      tickerMenu.value = null
    }
  }, interval)
}

// Action: กินเมนูนี้
function acceptMenu(menu: EnrichedMenu) {
  router.push({
    path: '/expenses/add',
    query: {
      restaurant_id: menu.restaurant_id,
      menu_id: menu.id,
      price: menu.price
    }
  })
}

// Fast filter modifications
function raiseBudget(amount: number) {
  budgetMode.value = 'custom'
  budgetCeiling.value += amount
  savePrefs()
}

function clearFilters() {
  selectedRestaurantId.value = null
  excludeRecent.value = false
  budgetMode.value = 'unlimited'
  savePrefs()
}

// Category icons
function getCategoryIcon(name: string) {
  const n = name.toLowerCase()
  if (n.includes('ก๋วยเตี๋ยว') || n.includes('บะหมี่') || n.includes('เส้น')) return '🍜'
  if (n.includes('น้ำ') || n.includes('ชา') || n.includes('กาแฟ')) return '🧋'
  if (n.includes('ขนม') || n.includes('ทอด') || n.includes('ลูกชิ้น')) return '🥪'
  return '🍚'
}
</script>

<template>
  <div class="roulette-page">
    <!-- Header -->
    <div class="roulette-header">
      <div class="header-icon-badge">🎲</div>
      <div>
        <h1 class="page-title">วันนี้กินอะไรดี?</h1>
        <p class="page-sub">ช่วยสุ่มมื้อเที่ยงจากร้านและเมนูจริงในโรงเรียน</p>
      </div>
    </div>

    <!-- 1. Localized Retryable Error State (Distinguished from empty menus) -->
    <div v-if="loadError" class="state-banner error-banner">
      <i class="pi pi-exclamation-triangle text-coral text-xl"></i>
      <div class="flex-1">
        <p class="font-bold text-coral m-0">ไม่สามารถโหลดข้อมูลเมนูอาหารได้</p>
        <p class="text-xs text-muted m-0 mt-0.5">{{ loadError }}</p>
      </div>
      <Button label="ลองใหม่อีกครั้ง" icon="pi pi-refresh" size="small" class="p-button-outlined" @click="loadRouletteData" />
    </div>

    <!-- 2. Loading State -->
    <div v-else-if="loading" class="loading-state">
      <i class="pi pi-spin pi-spinner text-3xl text-primary"></i>
      <p class="mt-3 text-muted">กำลังเตรียมเมนูอาหารในโรงเรียน...</p>
    </div>

    <!-- 3. Genuine Empty State: No restaurants or menus in database -->
    <div v-else-if="allMenus.length === 0" class="empty-state-card">
      <div class="empty-emoji">🍽️</div>
      <h2 class="empty-title">ยังไม่มีเมนูในระบบ</h2>
      <p class="empty-desc">
        คุณยังไม่มีร้านอาหารหรือเมนูที่บันทึกไว้ในระบบเลย เพิ่มร้านและเมนูโปรดก่อน เพื่อเริ่มสุ่มมื้อเที่ยงได้นะ!
      </p>
      <router-link to="/manage-menus" class="add-menu-cta-btn">
        <i class="pi pi-plus"></i>
        เพิ่มร้านและเมนูโรงเรียน
      </router-link>
    </div>

    <!-- 4. Main Roulette Content (When menus exist) -->
    <template v-else>
      <!-- FILTER PANEL -->
      <section class="filter-panel" aria-label="ตัวกรองการสุ่มเมนู">
        <div class="panel-header">
          <span class="panel-title">
            <i class="pi pi-sliders-h"></i>
            ตัวกรองก่อนสุ่ม
          </span>
          <span class="matching-count">
            มี {{ eligibleMenus.length }} เมนูที่เข้าเกณฑ์
          </span>
        </div>

        <!-- 1. Budget Ceiling Filter -->
        <div class="filter-item">
          <div class="filter-label-row">
            <label class="filter-label">เพดานงบประมาณ:</label>
            <span class="budget-tag" v-if="budgetMode === 'custom'">
              ไม่เกิน {{ formatTHB(budgetCeiling) }}
            </span>
            <span class="budget-tag" v-else>ไม่จำกัดงบ</span>
          </div>

          <!-- Quick Budget Preset Buttons -->
          <div class="budget-presets">
            <button 
              type="button" 
              class="preset-btn"
              :class="{ 'btn-active': budgetMode === 'custom' && budgetCeiling === 40 }"
              @click="budgetMode = 'custom'; budgetCeiling = 40; savePrefs()"
            >
              ฿40
            </button>
            <button 
              type="button" 
              class="preset-btn"
              :class="{ 'btn-active': budgetMode === 'custom' && budgetCeiling === 50 }"
              @click="budgetMode = 'custom'; budgetCeiling = 50; savePrefs()"
            >
              ฿50
            </button>
            <button 
              type="button" 
              class="preset-btn"
              :class="{ 'btn-active': budgetMode === 'custom' && budgetCeiling === 60 }"
              @click="budgetMode = 'custom'; budgetCeiling = 60; savePrefs()"
            >
              ฿60
            </button>
            <button 
              v-if="(budgetStore.summary?.remaining_today || 0) > 0"
              type="button" 
              class="preset-btn btn-remaining"
              :class="{ 'btn-active': budgetMode === 'custom' && budgetCeiling === budgetStore.summary?.remaining_today }"
              @click="budgetMode = 'custom'; budgetCeiling = budgetStore.summary?.remaining_today || 50; savePrefs()"
            >
              ตามงบที่เหลือ (฿{{ budgetStore.summary?.remaining_today }})
            </button>
            <button 
              type="button" 
              class="preset-btn"
              :class="{ 'btn-active': budgetMode === 'unlimited' }"
              @click="budgetMode = 'unlimited'; savePrefs()"
            >
              ไม่จำกัด
            </button>
          </div>
        </div>

        <!-- 2. Restaurant Filter -->
        <div class="filter-item">
          <label class="filter-label">ร้านอาหาร:</label>
          <div class="restaurant-filter-chips">
            <button 
              type="button" 
              class="rf-chip"
              :class="{ 'rf-active': selectedRestaurantId === null }"
              @click="selectedRestaurantId = null; savePrefs()"
            >
              ทุกร้าน
            </button>
            <button 
              v-for="r in restaurantsStore.activeRestaurants"
              :key="r.id"
              type="button" 
              class="rf-chip"
              :class="{ 'rf-active': selectedRestaurantId === r.id }"
              @click="selectedRestaurantId = r.id; savePrefs()"
            >
              {{ r.name }}
            </button>
          </div>
        </div>

        <!-- 3. Exclude Recent Meals Toggle -->
        <div class="filter-item toggle-row">
          <label for="exclude-toggle" class="toggle-label">
            <span class="font-medium text-main">ไม่เอาเมนูที่เพิ่งกิน</span>
            <span class="text-xs text-muted block">ตัดเมนูที่คุณเพิ่งบันทึกไปเร็วๆ นี้ออก</span>
          </label>
          <input 
            id="exclude-toggle" 
            v-model="excludeRecent" 
            type="checkbox" 
            class="custom-toggle"
            @change="savePrefs"
          />
        </div>
      </section>

      <!-- EMPTY RESULTS WARNING: When no menu fits filters -->
      <section v-if="eligibleMenus.length === 0" class="no-match-card">
        <div class="no-match-emoji">🔍</div>
        <h3 class="no-match-title">ไม่พบเมนูที่เข้ากับตัวกรองนี้</h3>
        <p class="no-match-sub">
          อาจเป็นเพราะเพดานงบประมาณ ฿{{ budgetCeiling }} ต่ำกว่าราคาเมนูของร้านที่เลือก
        </p>

        <div class="quick-fix-row">
          <button type="button" class="fix-btn" @click="raiseBudget(10)">
            + เพิ่มงบ ฿10
          </button>
          <button type="button" class="fix-btn" @click="raiseBudget(20)">
            + เพิ่มงบ ฿20
          </button>
          <button type="button" class="fix-btn fix-clear" @click="clearFilters">
            ล้างตัวกรองทั้งหมด
          </button>
        </div>
      </section>

      <!-- ROULETTE STAGE & RESULT CARD -->
      <section v-else class="roulette-stage">
        <!-- Spinning animation state -->
        <div v-if="isSpinning" class="spinning-box" aria-live="polite">
          <div class="spinner-card-deck">
            <div class="spinning-card">
              <span class="spinning-emoji">{{ getCategoryIcon(tickerMenu?.name || '') }}</span>
              <span class="spinning-menu-name">{{ tickerMenu?.name || 'กำลังสุ่ม...' }}</span>
              <span class="spinning-restaurant">{{ tickerMenu?.restaurantName || '' }}</span>
            </div>
          </div>
          <span class="spinning-hint">กำลังคัดเลือกเมนูที่ใช่...</span>
        </div>

        <!-- Winner Result Card -->
        <div v-else-if="selectedResult" class="result-card" role="region" aria-label="ผลการสุ่มอาหาร">
          <div class="result-badge-top">
            <span class="result-reason">{{ recommendationReason }}</span>
          </div>

          <div class="result-body">
            <div class="result-food-icon">
              {{ getCategoryIcon(selectedResult.name) }}
            </div>
            <h2 class="result-menu-name">{{ selectedResult.name }}</h2>
            <p class="result-restaurant-name">
              <i class="pi pi-shop"></i>
              {{ selectedResult.restaurantName }}
            </p>
            <div class="result-price-tag">
              {{ formatTHB(selectedResult.price) }}
            </div>
          </div>

          <!-- Budget Fit Feedback Line -->
          <div class="budget-fit-pill" :class="budgetFitStatus.fits ? 'fit-good' : 'fit-warning'">
            <i :class="budgetFitStatus.fits ? 'pi pi-check-circle' : 'pi pi-exclamation-circle'"></i>
            <span>{{ budgetFitStatus.label }}</span>
          </div>

          <!-- 3 CORE ACTIONS -->
          <div class="result-actions-stack">
            <!-- 1. กินเมนูนี้ -->
            <button 
              type="button" 
              class="action-btn-primary" 
              @click="acceptMenu(selectedResult)"
            >
              <i class="pi pi-check"></i>
              กินเมนูนี้ (ไปบันทึกรายจ่าย)
            </button>

            <div class="secondary-actions-row">
              <!-- 2. สุ่มใหม่ -->
              <button 
                type="button" 
                class="action-btn-reroll" 
                @click="spinRoulette"
              >
                <i class="pi pi-refresh"></i>
                สุ่มใหม่
              </button>

              <!-- 3. ดูเมนูทั้งหมด -->
              <button 
                type="button" 
                class="action-btn-browse" 
                @click="showAllMatchingModal = true"
              >
                <i class="pi pi-list"></i>
                ดูเมนูทั้งหมด ({{ eligibleMenus.length }})
              </button>
            </div>
          </div>
        </div>

        <!-- Initial Pre-Spin Card -->
        <div v-else class="pre-spin-card">
          <div class="pre-spin-graphic">
            <span class="dice-icon">🎲</span>
          </div>
          <h2 class="pre-spin-heading">กดปุ่มด้านล่างเพื่อเริ่มสุ่ม!</h2>
          <p class="pre-spin-sub">ระบบจะเลือก 1 เมนูจาก {{ eligibleMenus.length }} เมนูที่อยู่ในเงื่อนไขของคุณ</p>
          <button 
            type="button" 
            class="big-spin-btn"
            @click="spinRoulette"
          >
            <i class="pi pi-sparkles"></i>
            สุ่มมื้อเที่ยงตอนนี้
          </button>
        </div>
      </section>

      <!-- ALL MATCHING MENUS MODAL / DRAWER -->
      <div v-if="showAllMatchingModal" class="modal-overlay" @click="showAllMatchingModal = false" role="dialog" aria-modal="true">
        <div class="modal-sheet" @click.stop>
          <div class="sheet-top">
            <div>
              <h3 class="sheet-title">เมนูที่เข้าเกณฑ์ทั้งหมด</h3>
              <p class="sheet-sub">พบทั้งหมด {{ eligibleMenus.length }} เมนู</p>
            </div>
            <button type="button" class="close-btn" @click="showAllMatchingModal = false">✕</button>
          </div>

          <div class="menus-scroll-list">
            <div 
              v-for="m in eligibleMenus" 
              :key="m.id" 
              class="modal-menu-row"
              @click="acceptMenu(m)"
            >
              <div class="flex items-center gap-3">
                <span class="text-xl">{{ getCategoryIcon(m.name) }}</span>
                <div>
                  <div class="font-bold text-main">{{ m.name }}</div>
                  <div class="text-xs text-muted">{{ m.restaurantName }}</div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span class="font-bold text-primary">{{ formatTHB(m.price) }}</span>
                <i class="pi pi-chevron-right text-muted text-xs"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.roulette-page {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding-bottom: 2rem;
}

.roulette-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon-badge {
  width: 44px;
  height: 44px;
  border-radius: var(--border-radius-sm);
  background: var(--mango-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.page-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
}

.page-sub {
  font-size: 0.775rem;
  color: var(--text-muted);
  margin: 0.15rem 0 0;
}

/* State banners */
.state-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: var(--border-radius);
  background: #ffffff;
}

.error-banner {
  background: var(--warning-coral-light);
  border: 1px solid #FECACA;
  color: var(--warning-coral);
}

.loading-state {
  text-align: center;
  padding: 3rem 1rem;
}

/* Empty state */
.empty-state-card {
  background: #ffffff;
  border: 1px dashed var(--surface-border);
  border-radius: var(--border-radius-lg);
  padding: 2.5rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-emoji {
  font-size: 3rem;
  margin-bottom: 0.75rem;
}

.empty-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 0.5rem;
}

.empty-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0 0 1.5rem;
  max-width: 340px;
  line-height: 1.4;
}

.add-menu-cta-btn {
  background: var(--primary-color);
  color: #ffffff;
  border-radius: var(--border-radius);
  padding: 0.75rem 1.5rem;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-height: 44px;
}

/* Filter panel */
.filter-panel {
  background: #ffffff;
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius-lg);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--surface-border);
  padding-bottom: 0.6rem;
}

.panel-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.matching-count {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.filter-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
}

.budget-tag {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--primary-color);
}

.budget-presets {
  display: flex;
  gap: 0.4rem;
  overflow-x: auto;
  padding-bottom: 0.25rem;
}

.preset-btn {
  background: var(--surface-hover);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius-full);
  padding: 0.35rem 0.75rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-main);
  cursor: pointer;
  white-space: nowrap;
  font-family: inherit;
  min-height: 38px;
  transition: all 0.15s ease;
}

.preset-btn:hover {
  background: var(--primary-light);
  border-color: var(--primary-color);
}

.btn-active {
  background: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
  color: #ffffff !important;
}

.btn-remaining {
  border-color: var(--mango-accent);
  background: var(--mango-light);
  color: #B8781B;
}

.restaurant-filter-chips {
  display: flex;
  gap: 0.4rem;
  overflow-x: auto;
  padding-bottom: 0.25rem;
}

.rf-chip {
  background: var(--surface-hover);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius-full);
  padding: 0.35rem 0.75rem;
  font-size: 0.775rem;
  font-weight: 500;
  color: var(--text-main);
  cursor: pointer;
  white-space: nowrap;
  font-family: inherit;
  min-height: 38px;
  transition: all 0.15s ease;
}

.rf-chip:hover {
  border-color: var(--primary-color);
}

.rf-active {
  background: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
  color: #ffffff !important;
  font-weight: 600;
}

.toggle-row {
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.5rem;
  border-top: 1px dashed var(--surface-border);
}

.toggle-label {
  cursor: pointer;
}

.custom-toggle {
  width: 20px;
  height: 20px;
  accent-color: var(--primary-color);
  cursor: pointer;
}

/* No match state */
.no-match-card {
  background: #ffffff;
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius-lg);
  padding: 2rem 1rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.no-match-emoji {
  font-size: 2.25rem;
  margin-bottom: 0.5rem;
}

.no-match-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 0.35rem;
}

.no-match-sub {
  font-size: 0.8rem;
  color: var(--text-muted);
  max-width: 300px;
  margin: 0 0 1.25rem;
}

.quick-fix-row {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.fix-btn {
  background: var(--primary-light);
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
  border-radius: var(--border-radius-full);
  padding: 0.4rem 0.85rem;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  min-height: 40px;
  font-family: inherit;
}

.fix-clear {
  background: var(--surface-hover);
  border-color: var(--surface-border);
  color: var(--text-muted);
}

/* Roulette stage */
.roulette-stage {
  display: flex;
  flex-direction: column;
}

/* Pre-spin */
.pre-spin-card {
  background: #ffffff;
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius-lg);
  padding: 2.5rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4px 16px rgba(27, 77, 62, 0.05);
}

.pre-spin-graphic {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--mango-light);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.dice-icon {
  font-size: 2.5rem;
}

.pre-spin-heading {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 0.35rem;
}

.pre-spin-sub {
  font-size: 0.8rem;
  color: var(--text-muted);
  max-width: 280px;
  margin: 0 0 1.5rem;
}

.big-spin-btn {
  background: linear-gradient(135deg, var(--mango-accent) 0%, #D97706 100%);
  color: #ffffff;
  border: none;
  border-radius: var(--border-radius);
  padding: 0.85rem 2rem;
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-family: inherit;
  box-shadow: 0 4px 14px rgba(229, 169, 60, 0.4);
  min-height: 52px;
  transition: transform 0.15s ease;
}

.big-spin-btn:active {
  transform: scale(0.96);
}

/* Spinning box */
.spinning-box {
  background: #ffffff;
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius-lg);
  padding: 2.5rem 1rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.spinning-card {
  background: var(--surface-hover);
  border: 2px dashed var(--primary-color);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  width: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.spinning-emoji {
  font-size: 2.5rem;
}

.spinning-menu-name {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--primary-color);
}

.spinning-restaurant {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.spinning-hint {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 1rem;
}

/* Result card */
.result-card {
  background: #ffffff;
  border: 2px solid var(--mango-accent);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 8px 24px rgba(229, 169, 60, 0.15);
  animation: revealCard 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes revealCard {
  from { transform: scale(0.92); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.result-badge-top {
  margin-bottom: 0.75rem;
}

.result-reason {
  background: #FEF3C7;
  color: #92400E;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  display: inline-block;
}

.result-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}

.result-food-icon {
  font-size: 3.5rem;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.result-menu-name {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-main);
  margin: 0;
  line-height: 1.2;
}

.result-restaurant-name {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0.35rem 0 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.result-price-tag {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--primary-color);
}

.budget-fit-pill {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.85rem;
  border-radius: var(--border-radius-full);
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.fit-good {
  background: #ECFDF5;
  color: #065F46;
  border: 1px solid #A7F3D0;
}

.fit-warning {
  background: #FFFBEB;
  color: #B45309;
  border: 1px solid #FDE68A;
}

/* Actions Stack */
.result-actions-stack {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.action-btn-primary {
  width: 100%;
  background: var(--primary-color);
  color: #ffffff;
  border: none;
  border-radius: var(--border-radius);
  padding: 0.85rem;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-family: inherit;
  box-shadow: 0 4px 12px rgba(27, 77, 62, 0.25);
  min-height: 48px;
}

.secondary-actions-row {
  display: flex;
  gap: 0.6rem;
  width: 100%;
}

.action-btn-reroll {
  flex: 1;
  background: var(--mango-light);
  border: 1.5px solid var(--mango-accent);
  color: #B8781B;
  border-radius: var(--border-radius);
  padding: 0.65rem;
  font-size: 0.875rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-family: inherit;
  min-height: 44px;
}

.action-btn-browse {
  flex: 1;
  background: #ffffff;
  border: 1px solid var(--surface-border);
  color: var(--text-main);
  border-radius: var(--border-radius);
  padding: 0.65rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-family: inherit;
  min-height: 44px;
}

/* All matching modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 100;
  display: flex;
  align-items: flex-end;
}

.modal-sheet {
  background: #ffffff;
  width: 100%;
  max-height: 80vh;
  border-radius: 20px 20px 0 0;
  padding: 1.25rem;
  padding-bottom: max(1.5rem, env(safe-area-inset-bottom, 1.5rem));
  display: flex;
  flex-direction: column;
  animation: slideUp 0.25s ease-out;
}

.sheet-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.sheet-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
}

.sheet-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: 0.15rem 0 0;
}

.close-btn {
  background: #f1f5f9;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  cursor: pointer;
  color: #64748b;
  font-size: 0.85rem;
}

.menus-scroll-list {
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 60vh;
}

.modal-menu-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  cursor: pointer;
  min-height: 52px;
}

.modal-menu-row:hover {
  background: var(--surface-hover);
  border-color: var(--primary-color);
}
</style>
