<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBudgetStore } from '@/stores/budget'
import { useExpensesStore } from '@/stores/expenses'
import { useAnalyticsStore } from '@/stores/analytics'
import { useFormat } from '@/composables/useFormat'
import Button from 'primevue/button'

const router = useRouter()
const { formatTHB, formatDateTH } = useFormat()
const authStore = useAuthStore()
const budgetStore = useBudgetStore()
const expensesStore = useExpensesStore()
const analyticsStore = useAnalyticsStore()

const loading = ref(true)
const budgetFailed = ref(false)
const expensesFailed = ref(false)
const analyticsFailed = ref(false)
const settingBudget = ref(false)

// Retrying individual sections
const retryingBudget = ref(false)
const retryingExpenses = ref(false)

// Current date & greeting
const todayDateStr = computed(() => formatDateTH(new Date()))

const greeting = computed(() => {
  const hour = new Date().getHours()
  const name = authStore.user?.username || 'เพื่อนนักเรียน'
  if (hour < 11) return `สวัสดีตอนเช้า, ${name} ☀️`
  if (hour < 14) return `พักเที่ยงแล้วนะ, ${name} 🍱`
  if (hour < 17) return `สวัสดีตอนบ่าย, ${name} 🍵`
  return `สวัสดีตอนเย็น, ${name} 🌙`
})

async function loadDashboardData() {
  loading.value = true
  budgetFailed.value = false
  expensesFailed.value = false
  analyticsFailed.value = false

  const results = await Promise.allSettled([
    budgetStore.fetchBudgetSummary(),
    expensesStore.fetchExpenses({ per_page: 6 }),
    analyticsStore.fetchSummary(),
    expensesStore.refreshOfflineQueueCount()
  ])

  if (results[0].status === 'rejected') {
    budgetFailed.value = true
  }
  if (results[1].status === 'rejected') {
    expensesFailed.value = true
  }
  if (results[2].status === 'rejected') {
    analyticsFailed.value = true
  }

  loading.value = false
}

async function retryBudget() {
  retryingBudget.value = true
  try {
    await budgetStore.fetchBudgetSummary()
    budgetFailed.value = false
  } catch {
    budgetFailed.value = true
  } finally {
    retryingBudget.value = false
  }
}

async function retryExpenses() {
  retryingExpenses.value = true
  try {
    await expensesStore.fetchExpenses({ per_page: 6 })
    expensesFailed.value = false
  } catch {
    expensesFailed.value = true
  } finally {
    retryingExpenses.value = false
  }
}

onMounted(() => {
  loadDashboardData()
})

// Budget computations
const dailyBudget = computed(() => budgetStore.summary?.daily_budget || 0)
const spentToday = computed(() => budgetStore.summary?.spent_today || 0)
const remainingToday = computed(() => {
  if (!budgetStore.summary) return 0
  return budgetStore.summary.remaining_today
})

const isOverBudget = computed(() => {
  return dailyBudget.value > 0 && spentToday.value > dailyBudget.value
})

const budgetUsagePercent = computed(() => {
  if (dailyBudget.value <= 0) return 0
  return Math.min(Math.round((spentToday.value / dailyBudget.value) * 100), 100)
})

const budgetRawPercent = computed(() => {
  if (dailyBudget.value <= 0) return 0
  return Math.round((spentToday.value / dailyBudget.value) * 100)
})

const isNearLimit = computed(() => {
  return budgetRawPercent.value >= 80 && budgetRawPercent.value < 100
})

// Plain Thai supportive budget feedback
const budgetFeedback = computed(() => {
  if (dailyBudget.value <= 0) {
    return 'ยังไม่ได้ตั้งงบมื้อเที่ยงรายวัน เลือกงบด้านล่างได้เลย'
  }
  if (isOverBudget.value) {
    const overAmount = spentToday.value - dailyBudget.value
    return `เกินงบ ${formatTHB(overAmount)} แล้ว ไม่เป็นไร พรุ่งนี้เริ่มใหม่ได้!`
  }
  if (isNearLimit.value) {
    return `ใกล้ถึงงบแล้ว (ใช้ไป ${budgetRawPercent.value}%) ลองเลือกเมนูประหยัดมื้อต่อไป`
  }
  return `วันนี้ยังเหลือ ${formatTHB(remainingToday.value)} คุมงบได้ดีมาก!`
})

// Category emoji icons
function getCategoryIcon(cat?: string) {
  switch (cat) {
    case 'rice': return '🍚'
    case 'noodle': return '🍜'
    case 'snack': return '🥪'
    case 'drink': return '🧋'
    case 'fruit': return '🍉'
    default: return '🍴'
  }
}

// Quick presets for setting budget
async function handleQuickSetBudget(amount: number) {
  settingBudget.value = true
  try {
    await budgetStore.updateBudget(amount)
    await budgetStore.fetchBudgetSummary()
    budgetFailed.value = false
  } catch (err: any) {
    // handled in store
  } finally {
    settingBudget.value = false
  }
}

// Quick re-order / frequent items derived from real expense history
const quickReorderItems = computed(() => {
  const map = new Map<string, { menuName: string; restaurantName: string; restaurantId: number; menuId: number; price: number; category: any; count: number }>()
  
  for (const exp of expensesStore.expenses) {
    if (exp.menu && exp.menu_id) {
      const key = `${exp.restaurant_id}-${exp.menu_id}`
      const existing = map.get(key)
      if (existing) {
        existing.count += 1
      } else {
        map.set(key, {
          menuName: exp.menu.name,
          restaurantName: exp.restaurant?.name || 'ร้านประจำ',
          restaurantId: exp.restaurant_id,
          menuId: exp.menu_id,
          price: exp.amount,
          category: exp.category,
          count: 1
        })
      }
    }
  }
  return Array.from(map.values()).slice(0, 3)
})

function quickAdd(item: { restaurantId: number; menuId: number; price: number; category: string }) {
  router.push({
    path: '/expenses/add',
    query: {
      restaurant_id: item.restaurantId,
      menu_id: item.menuId,
      price: item.price,
      category: item.category
    }
  })
}
</script>

<template>
  <div class="today-dashboard">
    <!-- Header Greeting & Date -->
    <section class="dashboard-greeting">
      <div class="greeting-content">
        <h1 class="greeting-title">{{ greeting }}</h1>
        <p class="greeting-date">
          <i class="pi pi-calendar"></i>
          {{ todayDateStr }}
        </p>
      </div>
    </section>

    <!-- Global Network Failure when all critical calls fail -->
    <div v-if="budgetFailed && expensesFailed" class="state-card error-card">
      <i class="pi pi-wifi text-coral text-xl"></i>
      <div class="state-text flex-1">
        <p class="font-bold text-coral">ไม่สามารถเชื่อมต่อข้อมูลได้</p>
        <p class="text-xs text-muted">เครือข่ายขัดข้อง กรุณาตรวจสอบสัญญาณเน็ตแล้วลองใหม่</p>
      </div>
      <Button label="โหลดใหม่ทั้งหมด" icon="pi pi-refresh" size="small" class="p-button-outlined" @click="loadDashboardData" />
    </div>

    <!-- Skeleton Loading State -->
    <div v-if="loading && !budgetStore.summary" class="skeleton-container" aria-label="กำลังโหลดข้อมูล">
      <div class="skeleton-card skeleton-budget-card"></div>
      <div class="skeleton-actions">
        <div class="skeleton-btn"></div>
        <div class="skeleton-btn"></div>
      </div>
      <div class="skeleton-card skeleton-list-card"></div>
    </div>

    <template v-else>
      <!-- PRIMARY TODAY BUDGET CARD -->
      <section v-if="budgetFailed && !budgetStore.summary" class="today-budget-card localized-error-card">
        <div class="flex items-center gap-3">
          <i class="pi pi-exclamation-circle text-coral text-2xl"></i>
          <div class="flex-1">
            <h3 class="font-bold text-main m-0">ไม่สามารถโหลดข้อมูลงบประมาณได้</h3>
            <p class="text-xs text-muted m-0 mt-1">สัญญาณขัดข้อง ไม่สามารถดึงงบคงเหลือวันนี้ได้</p>
          </div>
          <Button 
            label="ลองใหม่" 
            icon="pi pi-refresh" 
            size="small" 
            :loading="retryingBudget" 
            class="p-button-outlined"
            @click="retryBudget" 
          />
        </div>
      </section>

      <section v-else class="today-budget-card" :class="{ 'is-over': isOverBudget, 'is-near': isNearLimit }">
        <div class="card-header-bar">
          <span class="card-label">
            <span class="pulse-dot" :class="isOverBudget ? 'dot-red' : (isNearLimit ? 'dot-yellow' : 'dot-green')"></span>
            งบประมาณวันนี้
          </span>
          <router-link to="/budget" class="edit-budget-btn" aria-label="แก้ไขงบรายวัน">
            <span class="budget-target-pill">งบวันละ {{ formatTHB(dailyBudget) }}</span>
            <i class="pi pi-pencil"></i>
          </router-link>
        </div>

        <!-- Big Remaining/Spent Numbers -->
        <div class="budget-figures">
          <div class="remaining-group">
            <span class="figure-label">{{ isOverBudget ? 'เกินงบไปแล้ว' : 'ยอดคงเหลือวันนี้' }}</span>
            <div class="figure-amount" :class="isOverBudget ? 'text-coral' : 'text-mango'">
              {{ isOverBudget ? formatTHB(spentToday - dailyBudget) : formatTHB(remainingToday) }}
            </div>
          </div>
          
          <div class="spent-badge">
            <span class="spent-label">ใช้ไปแล้ว</span>
            <span class="spent-value">{{ formatTHB(spentToday) }}</span>
          </div>
        </div>

        <!-- Expressive Visual Progress Bar -->
        <div class="progress-section" v-if="dailyBudget > 0">
          <div class="progress-track">
            <div 
              class="progress-fill" 
              :class="{ 'fill-over': isOverBudget, 'fill-near': isNearLimit, 'fill-good': !isOverBudget && !isNearLimit }"
              :style="{ width: `${budgetUsagePercent}%` }"
            ></div>
          </div>
          <div class="progress-labels">
            <span>0%</span>
            <span class="usage-text">{{ budgetRawPercent }}% ของงบ</span>
            <span>100%</span>
          </div>
        </div>

        <!-- Plain Thai Budget Feedback Alert -->
        <div 
          class="feedback-banner" 
          :class="{ 'feedback-over': isOverBudget, 'feedback-near': isNearLimit, 'feedback-good': !isOverBudget && !isNearLimit }"
        >
          <span class="feedback-icon">{{ isOverBudget ? '⚠️' : (isNearLimit ? '⏳' : '✨') }}</span>
          <span class="feedback-text">{{ budgetFeedback }}</span>
        </div>

        <!-- Quick Budget Setup when dailyBudget is 0 -->
        <div v-if="dailyBudget <= 0" class="setup-budget-box">
          <p class="setup-title">💡 ตั้งงบต่อวันของคุณเพื่อเริ่มต้นคุมค่ากิน:</p>
          <div class="preset-buttons">
            <button 
              type="button" 
              class="preset-chip" 
              :disabled="settingBudget"
              @click="handleQuickSetBudget(50)"
            >
              ฿50 / วัน
            </button>
            <button 
              type="button" 
              class="preset-chip chip-popular" 
              :disabled="settingBudget"
              @click="handleQuickSetBudget(60)"
            >
              ฿60 (แนะนำ)
            </button>
            <button 
              type="button" 
              class="preset-chip" 
              :disabled="settingBudget"
              @click="handleQuickSetBudget(80)"
            >
              ฿80 / วัน
            </button>
          </div>
        </div>
      </section>

      <!-- PRIMARY & SECONDARY ACTIONS -->
      <section class="main-actions-grid">
        <!-- 1. Strongest Primary Action: บันทึกมื้อกลางวัน -->
        <router-link to="/expenses/add" class="cta-primary-btn" aria-label="บันทึกมื้อกลางวันทันที">
          <div class="cta-icon-wrap">
            <i class="pi pi-plus"></i>
          </div>
          <div class="cta-content">
            <span class="cta-title">บันทึกมื้อกลางวัน</span>
            <span class="cta-desc">เร็วใน 5 วินาทีระหว่างพักเที่ยง</span>
          </div>
          <i class="pi pi-chevron-right cta-arrow"></i>
        </router-link>

        <!-- 2. Equally Discoverable Secondary Action: วันนี้กินอะไรดี? -->
        <router-link to="/what-to-eat" class="cta-roulette-btn" aria-label="สุ่มเมนูอาหารวันนี้">
          <div class="cta-roulette-badge">
            <span class="roulette-emoji">🎲</span>
          </div>
          <div class="cta-content">
            <div class="flex items-center gap-1">
              <span class="cta-roulette-title">วันนี้กินอะไรดี?</span>
              <span class="sparkle-tag">สุ่มเมนู</span>
            </div>
            <span class="cta-desc">สุ่มจากร้านโรงอาหารตามงบที่เหลือ</span>
          </div>
          <i class="pi pi-sparkles cta-sparkle-icon"></i>
        </router-link>
      </section>

      <!-- QUICK RE-ORDER CHIPS (Derived from real student history) -->
      <section v-if="quickReorderItems.length > 0" class="quick-reorder-section">
        <div class="section-title-row">
          <span class="section-badge-icon">⚡</span>
          <h2 class="section-title">มื้อที่คุณสั่งบ่อย (บันทึกซ้ำเร็ว)</h2>
        </div>
        <div class="reorder-chips-scroll">
          <button 
            v-for="item in quickReorderItems" 
            :key="item.menuId" 
            type="button"
            class="reorder-chip-card"
            @click="quickAdd(item)"
          >
            <span class="reorder-chip-icon">{{ getCategoryIcon(item.category) }}</span>
            <div class="reorder-chip-info">
              <span class="reorder-menu-name">{{ item.menuName }}</span>
              <span class="reorder-shop-name">{{ item.restaurantName }}</span>
            </div>
            <span class="reorder-price">{{ formatTHB(item.price) }}</span>
          </button>
        </div>
      </section>

      <!-- RECENT TRANSACTIONS (Compact, food-oriented) -->
      <section class="recent-expenses-section">
        <div class="section-title-row">
          <div class="flex items-center gap-2">
            <span class="section-badge-icon">🕒</span>
            <h2 class="section-title">รายการล่าสุด</h2>
          </div>
          <router-link v-if="expensesStore.expenses.length > 0" to="/history" class="see-all-link">
            ดูทั้งหมด
            <i class="pi pi-angle-right"></i>
          </router-link>
        </div>

        <!-- 1. Localized Error State for Expenses (Distinguished from empty state) -->
        <div v-if="expensesFailed && expensesStore.expenses.length === 0" class="state-card error-card">
          <i class="pi pi-exclamation-triangle text-coral"></i>
          <div class="state-text flex-1">
            <p class="font-bold text-coral m-0">ไม่สามารถโหลดรายการล่าสุดได้</p>
            <p class="text-xs text-muted m-0 mt-0.5">เกิดข้อผิดพลาดในการดึงข้อมูลจากเซิร์ฟเวอร์</p>
          </div>
          <Button 
            label="ลองใหม่" 
            icon="pi pi-refresh" 
            size="small" 
            :loading="retryingExpenses" 
            class="p-button-outlined" 
            @click="retryExpenses" 
          />
        </div>

        <!-- 2. Genuine Empty State (Only when request succeeded and items are 0) -->
        <div v-else-if="expensesStore.expenses.length === 0" class="empty-expense-box">
          <div class="empty-icon-circle">🍱</div>
          <h3 class="empty-heading">ยังไม่มีบันทึกมื้อเที่ยงวันนี้</h3>
          <p class="empty-sub">เพิ่งซื้อข้าวเที่ยงมาใช่ไหม? กดปุ่มบันทึกด้านบนได้เลย</p>
          <router-link to="/expenses/add" class="empty-cta-btn">
            <i class="pi pi-plus"></i>
            บันทึกรายการแรก
          </router-link>
        </div>

        <!-- 3. Compact Expenses List -->
        <div v-else class="expenses-compact-list">
          <div 
            v-for="exp in expensesStore.expenses" 
            :key="exp.id" 
            class="compact-expense-item"
            @click="router.push(`/expenses/${exp.id}/edit`)"
          >
            <div class="item-icon-box">
              <span class="category-emoji">{{ getCategoryIcon(exp.category) }}</span>
            </div>
            <div class="item-details">
              <span class="item-menu-name">{{ exp.menu?.name || 'มื้ออาหาร' }}</span>
              <div class="item-meta">
                <span class="item-restaurant">{{ exp.restaurant?.name || 'โรงอาหาร' }}</span>
                <span class="meta-dot">•</span>
                <span class="item-date">{{ new Date(exp.date).toLocaleDateString('th-TH', { month: 'short', day: 'numeric' }) }}</span>
              </div>
            </div>
            <div class="item-amount-wrap">
              <span class="item-amount">-{{ formatTHB(exp.amount) }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- SECONDARY MONTHLY SUMMARY (Subtle pill, below the fold) -->
      <section v-if="analyticsStore.summary && !analyticsFailed" class="secondary-monthly-pill">
        <div class="pill-left">
          <i class="pi pi-chart-pie text-muted"></i>
          <span class="pill-label">ยอดสะสมเดือนนี้</span>
          <span class="pill-value">{{ formatTHB(analyticsStore.summary.spent_month || 0) }}</span>
        </div>
        <router-link to="/analytics" class="pill-link">
          ดูสถิติ
          <i class="pi pi-arrow-right"></i>
        </router-link>
      </section>
    </template>
  </div>
</template>

<style scoped>
.today-dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 600px;
  margin: 0 auto;
}

/* Greeting */
.dashboard-greeting {
  padding: 0.25rem 0.25rem 0;
}

.greeting-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
  line-height: 1.25;
}

.greeting-date {
  font-size: 0.825rem;
  color: var(--text-muted);
  margin: 0.25rem 0 0;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

/* Primary Today Budget Card */
.today-budget-card {
  background: #ffffff;
  border-radius: var(--border-radius-lg);
  padding: 1.25rem;
  border: 1px solid var(--surface-border);
  box-shadow: 0 4px 16px rgba(27, 77, 62, 0.06);
  position: relative;
  transition: all 0.2s ease;
}

.localized-error-card {
  border-color: rgba(220, 38, 38, 0.4);
  background: #FFF5F5;
}

.today-budget-card.is-over {
  border-color: rgba(220, 38, 38, 0.3);
  background: linear-gradient(180deg, #ffffff 0%, #FFF5F5 100%);
}

.today-budget-card.is-near {
  border-color: rgba(229, 169, 60, 0.4);
  background: linear-gradient(180deg, #ffffff 0%, #FEFBF6 100%);
}

.card-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.card-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.dot-green { background-color: #10B981; box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2); }
.dot-yellow { background-color: var(--mango-accent); box-shadow: 0 0 0 3px rgba(229, 169, 60, 0.2); }
.dot-red { background-color: var(--warning-coral); box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.2); }

.edit-budget-btn {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  text-decoration: none;
  color: var(--text-muted);
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
  border-radius: var(--border-radius-full);
  background: var(--surface-hover);
  min-height: 28px;
  transition: all 0.15s ease;
}

.edit-budget-btn:hover {
  color: var(--primary-color);
  background: var(--primary-light);
}

.budget-figures {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 1rem;
}

.remaining-group {
  display: flex;
  flex-direction: column;
}

.figure-label {
  font-size: 0.825rem;
  color: var(--text-muted);
  font-weight: 500;
}

.figure-amount {
  font-size: 2.15rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.1;
  margin-top: 0.15rem;
}

.text-mango {
  color: #B8781B;
}

.text-coral {
  color: var(--warning-coral);
}

.spent-badge {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  background: var(--surface-hover);
  padding: 0.35rem 0.75rem;
  border-radius: var(--border-radius-sm);
}

.spent-label {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.spent-value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-main);
}

/* Progress bar */
.progress-section {
  margin-bottom: 0.85rem;
}

.progress-track {
  width: 100%;
  height: 10px;
  background-color: #E2E8F0;
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.4s ease-out;
}

.fill-good {
  background: linear-gradient(90deg, #10B981 0%, #059669 100%);
}

.fill-near {
  background: linear-gradient(90deg, #F59E0B 0%, #D97706 100%);
}

.fill-over {
  background: linear-gradient(90deg, #EF4444 0%, #DC2626 100%);
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: var(--text-light);
  margin-top: 0.3rem;
  font-weight: 500;
}

.usage-text {
  color: var(--text-muted);
  font-weight: 600;
}

/* Feedback banner */
.feedback-banner {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.65rem 0.85rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.85rem;
  font-weight: 500;
  line-height: 1.35;
}

.feedback-good {
  background-color: #ECFDF5;
  color: #065F46;
  border: 1px solid #A7F3D0;
}

.feedback-near {
  background-color: var(--mango-light);
  color: #92400E;
  border: 1px solid #FDE68A;
}

.feedback-over {
  background-color: var(--warning-coral-light);
  color: #991B1B;
  border: 1px solid #FECACA;
}

.feedback-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
}

/* Setup budget box */
.setup-budget-box {
  margin-top: 1rem;
  padding-top: 0.85rem;
  border-top: 1px dashed var(--surface-border);
}

.setup-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-main);
  margin: 0 0 0.5rem;
}

.preset-buttons {
  display: flex;
  gap: 0.5rem;
}

.preset-chip {
  flex: 1;
  background: var(--surface-hover);
  border: 1px solid var(--surface-border);
  padding: 0.5rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-main);
  cursor: pointer;
  transition: all 0.15s ease;
  min-height: 44px;
}

.preset-chip:hover {
  border-color: var(--primary-color);
  background: var(--primary-light);
  color: var(--primary-color);
}

.chip-popular {
  background: var(--primary-light);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

/* Action Cards */
.main-actions-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.cta-primary-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: linear-gradient(135deg, var(--primary-color) 0%, #23654E 100%);
  color: #ffffff;
  padding: 1rem 1.25rem;
  border-radius: var(--border-radius);
  text-decoration: none;
  box-shadow: 0 4px 14px rgba(27, 77, 62, 0.25);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  min-height: 64px;
}

.cta-primary-btn:active {
  transform: scale(0.98);
}

.cta-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.2rem;
}

.cta-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.cta-title {
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.cta-desc {
  font-size: 0.75rem;
  opacity: 0.85;
}

.cta-arrow {
  font-size: 1rem;
  opacity: 0.7;
}

.cta-roulette-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #ffffff;
  border: 1.5px solid var(--mango-accent);
  color: var(--text-main);
  padding: 0.85rem 1.25rem;
  border-radius: var(--border-radius);
  text-decoration: none;
  box-shadow: 0 2px 8px rgba(229, 169, 60, 0.12);
  transition: transform 0.15s ease, background 0.15s ease;
  min-height: 56px;
}

.cta-roulette-btn:active {
  transform: scale(0.98);
}

.cta-roulette-badge {
  width: 40px;
  height: 40px;
  border-radius: var(--border-radius-sm);
  background-color: var(--mango-light);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.roulette-emoji {
  font-size: 1.35rem;
}

.cta-roulette-title {
  font-size: 1rem;
  font-weight: 700;
  color: #B8781B;
}

.sparkle-tag {
  background-color: #FEF3C7;
  color: #B45309;
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
}

.cta-sparkle-icon {
  color: var(--mango-accent);
  font-size: 1.1rem;
}

/* Quick Re-Order Section */
.quick-reorder-section {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 0.25rem;
}

.section-badge-icon {
  font-size: 1rem;
  margin-right: 0.35rem;
}

.section-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
}

.reorder-chips-scroll {
  display: flex;
  gap: 0.6rem;
  overflow-x: auto;
  padding-bottom: 0.35rem;
  -webkit-overflow-scrolling: touch;
}

.reorder-chip-card {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background: #ffffff;
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  min-height: 48px;
  transition: all 0.15s ease;
  font-family: inherit;
  text-align: left;
}

.reorder-chip-card:hover {
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.reorder-chip-icon {
  font-size: 1.25rem;
}

.reorder-chip-info {
  display: flex;
  flex-direction: column;
}

.reorder-menu-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-main);
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.reorder-shop-name {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.reorder-price {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-left: 0.25rem;
}

/* Recent expenses */
.recent-expenses-section {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.see-all-link {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--primary-color);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.2rem;
}

.empty-expense-box {
  background: #ffffff;
  border: 1px dashed var(--surface-border);
  border-radius: var(--border-radius-lg);
  padding: 2rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-icon-circle {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.empty-heading {
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 0.35rem;
  color: var(--text-main);
}

.empty-sub {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin: 0 0 1rem;
  max-width: 280px;
}

.empty-cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--primary-color);
  color: #ffffff;
  padding: 0.5rem 1.25rem;
  border-radius: var(--border-radius);
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 600;
  min-height: 44px;
}

.expenses-compact-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.compact-expense-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #ffffff;
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  padding: 0.75rem 1rem;
  cursor: pointer;
  min-height: 56px;
  transition: all 0.15s ease;
}

.compact-expense-item:hover {
  background: var(--surface-hover);
  border-color: #CBD5E1;
}

.item-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--surface-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.category-emoji {
  font-size: 1.25rem;
}

.item-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.item-menu-name {
  font-size: 0.925rem;
  font-weight: 600;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.meta-dot {
  opacity: 0.5;
}

.item-amount-wrap {
  text-align: right;
  flex-shrink: 0;
}

.item-amount {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-main);
}

/* Secondary monthly pill */
.secondary-monthly-pill {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  padding: 0.75rem 1rem;
  min-height: 44px;
}

.pill-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.825rem;
}

.pill-label {
  color: var(--text-muted);
}

.pill-value {
  font-weight: 700;
  color: var(--primary-color);
}

.pill-link {
  font-size: 0.775rem;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Error state */
.state-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: var(--border-radius);
  background: #ffffff;
  border: 1px solid var(--surface-border);
}

.error-card {
  border-color: rgba(220, 38, 38, 0.4);
  background: var(--warning-coral-light);
}

/* Skeletons */
.skeleton-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.skeleton-card {
  background: #e2e8f0;
  border-radius: var(--border-radius-lg);
  animation: pulse 1.5s infinite;
}

.skeleton-budget-card {
  height: 180px;
}

.skeleton-actions {
  display: flex;
  gap: 0.75rem;
}

.skeleton-btn {
  flex: 1;
  height: 56px;
  background: #e2e8f0;
  border-radius: var(--border-radius);
  animation: pulse 1.5s infinite;
}

.skeleton-list-card {
  height: 150px;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
</style>
