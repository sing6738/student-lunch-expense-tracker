<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRestaurantsStore } from '@/stores/restaurants'
import { useBudgetStore } from '@/stores/budget'
import { EXPENSE_CATEGORIES } from '@/utils/constants'
import { formatDateInput } from '@/utils/date'
import { formatTHB } from '@/utils/currency'
import type { Menu, Restaurant } from '@/types/restaurant'
import type { ExpenseCategory } from '@/types/expense'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'

interface Props {
  initialData?: any
  isEditing?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  initialData: () => ({}),
  isEditing: false,
})

const emit = defineEmits<{
  submit: [data: any]
  cancel: []
}>()

const restaurantsStore = useRestaurantsStore()
const budgetStore = useBudgetStore()

// State
const restaurantId = ref<number | null>(props.initialData?.restaurant_id ? Number(props.initialData.restaurant_id) : null)
const menuId = ref<number | null>(props.initialData?.menu_id ? Number(props.initialData.menu_id) : null)
const amount = ref<number>(props.initialData?.amount ? Number(props.initialData.amount) : (props.initialData?.price ? Number(props.initialData.price) : 0))
const category = ref<ExpenseCategory>(props.initialData?.category || 'rice')
const date = ref<string>(props.initialData?.date ? formatDateInput(props.initialData.date) : formatDateInput(new Date()))
const note = ref<string>(props.initialData?.note || '')

// Search filters
const restaurantSearch = ref('')
const menuSearch = ref('')
const menus = ref<Menu[]>([])
const loadingMenus = ref(false)

onMounted(async () => {
  await Promise.allSettled([
    restaurantsStore.fetchRestaurants(),
    budgetStore.fetchBudgetSummary()
  ])
  if (restaurantId.value) {
    loadMenusForRestaurant(restaurantId.value)
  }
})

// Filtered restaurants
const filteredRestaurants = computed(() => {
  const active = restaurantsStore.activeRestaurants
  if (!restaurantSearch.value.trim()) return active
  const q = restaurantSearch.value.toLowerCase()
  return active.filter(r => r.name.toLowerCase().includes(q))
})

// Filtered menus
const filteredMenus = computed(() => {
  if (!menuSearch.value.trim()) return menus.value
  const q = menuSearch.value.toLowerCase()
  return menus.value.filter(m => m.name.toLowerCase().includes(q))
})

// Selected restaurant & menu object
const selectedRestaurant = computed(() => {
  return restaurantsStore.restaurants.find(r => r.id === restaurantId.value) || null
})

const selectedMenu = computed(() => {
  return menus.value.find(m => m.id === menuId.value) || null
})

async function loadMenusForRestaurant(id: number) {
  loadingMenus.value = true
  try {
    const list = await restaurantsStore.fetchMenus(id)
    menus.value = list
    // If current menu is not in this restaurant's menu list, reset menuId unless in initial load with match
    if (menuId.value && !list.find(m => m.id === menuId.value)) {
      menuId.value = null
    }
  } finally {
    loadingMenus.value = false
  }
}

function handleSelectRestaurant(r: Restaurant) {
  restaurantId.value = r.id
  menuId.value = null
  loadMenusForRestaurant(r.id)
}

function handleSelectMenu(m: Menu) {
  menuId.value = m.id
  amount.value = m.price
  // Auto-infer category from menu name if applicable
  const n = m.name.toLowerCase()
  if (n.includes('ก๋วยเตี๋ยว') || n.includes('บะหมี่') || n.includes('เส้น') || n.includes('ราดหน้า') || n.includes('ผัดซีอิ๊ว')) {
    category.value = 'noodle'
  } else if (n.includes('น้ำ') || n.includes('ชา') || n.includes('กาแฟ') || n.includes('นม') || n.includes('โอวันติน')) {
    category.value = 'drink'
  } else if (n.includes('ผลไม้') || n.includes('แตงโม') || n.includes('มะม่วง')) {
    category.value = 'fruit'
  } else if (n.includes('ขนม') || n.includes('ลูกชิ้น') || n.includes('ไส้กรอก') || n.includes('ปัง')) {
    category.value = 'snack'
  } else {
    category.value = 'rice'
  }
}

// Quick price adjustment modifiers
function addModifier(extra: number) {
  amount.value = Math.max(0, (amount.value || 0) + extra)
}

// Real-time remaining budget calculations
const currentRemaining = computed(() => budgetStore.summary?.remaining_today || 0)
const projectedRemaining = computed(() => {
  return currentRemaining.value - (amount.value || 0)
})

const isProjectedOver = computed(() => {
  return projectedRemaining.value < 0
})

// Validation
const formErrors = ref<Record<string, string>>({})

function validate(): boolean {
  formErrors.value = {}
  if (!restaurantId.value) {
    formErrors.value.restaurant = 'กรุณาเลือกร้านอาหาร'
  }
  if (!menuId.value) {
    formErrors.value.menu = 'กรุณาเลือกเมนู'
  }
  if (!amount.value || amount.value <= 0) {
    formErrors.value.amount = 'กรุณาระบุจำนวนเงินมากกว่า 0'
  }
  return Object.keys(formErrors.value).length === 0
}

function handleSubmit() {
  if (!validate()) return
  emit('submit', {
    restaurant_id: restaurantId.value,
    menu_id: menuId.value,
    amount: amount.value,
    category: category.value,
    date: date.value,
    note: note.value.trim()
  })
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="quick-expense-form">
    <!-- Step 1: Restaurant Selection Chips -->
    <section class="form-section">
      <div class="section-label-row">
        <label class="section-heading">
          <span class="step-num">1</span>
          เลือกร้านอาหาร <span class="required">*</span>
        </label>
        <span v-if="selectedRestaurant" class="selected-badge">
          {{ selectedRestaurant.name }}
        </span>
      </div>

      <!-- Restaurant search or quick chips -->
      <div class="search-input-wrap">
        <i class="pi pi-search search-icon"></i>
        <input 
          v-model="restaurantSearch" 
          type="text" 
          placeholder="ค้นหาร้านอาหารในโรงเรียน..." 
          class="custom-search-input"
        />
        <button v-if="restaurantSearch" type="button" class="clear-btn" @click="restaurantSearch = ''">✕</button>
      </div>

      <div class="chips-container" role="radiogroup" aria-label="รายชื่อร้านอาหาร">
        <button
          v-for="r in filteredRestaurants"
          :key="r.id"
          type="button"
          class="chip-item"
          :class="{ 'chip-selected': restaurantId === r.id }"
          @click="handleSelectRestaurant(r)"
          :aria-checked="restaurantId === r.id"
        >
          <span class="chip-icon">🏬</span>
          <span class="chip-text">{{ r.name }}</span>
        </button>
      </div>
      <small v-if="formErrors.restaurant" class="p-error">{{ formErrors.restaurant }}</small>
    </section>

    <!-- Step 2: Menu Selection Cards/Chips -->
    <section class="form-section">
      <div class="section-label-row">
        <label class="section-heading">
          <span class="step-num">2</span>
          เลือกเมนูอาหาร <span class="required">*</span>
        </label>
        <span v-if="selectedMenu" class="selected-badge">
          {{ selectedMenu.name }} ({{ formatTHB(selectedMenu.price) }})
        </span>
      </div>

      <div v-if="!restaurantId" class="hint-card">
        <i class="pi pi-info-circle"></i>
        <span>แตะเลือกร้านอาหารด้านบนก่อนเพื่อดูเมนู</span>
      </div>

      <div v-else-if="loadingMenus" class="hint-card">
        <i class="pi pi-spin pi-spinner"></i>
        <span>กำลังโหลดรายการเมนู...</span>
      </div>

      <div v-else-if="menus.length === 0" class="hint-card">
        <i class="pi pi-exclamation-circle"></i>
        <div>
          <p class="m-0">ร้านนี้ยังไม่มีเมนูในระบบ</p>
          <router-link to="/manage-menus" class="text-xs font-semibold text-primary underline">
            เพิ่มเมนูของร้านนี้
          </router-link>
        </div>
      </div>

      <div v-else>
        <!-- Menu search if more than 4 items -->
        <div v-if="menus.length > 4" class="search-input-wrap mb-2">
          <i class="pi pi-search search-icon"></i>
          <input 
            v-model="menuSearch" 
            type="text" 
            placeholder="ค้นหาชื่อเมนู..." 
            class="custom-search-input"
          />
        </div>

        <div class="menu-grid" role="radiogroup" aria-label="รายการเมนู">
          <button
            v-for="m in filteredMenus"
            :key="m.id"
            type="button"
            class="menu-chip-card"
            :class="{ 'menu-selected': menuId === m.id }"
            @click="handleSelectMenu(m)"
            :aria-checked="menuId === m.id"
          >
            <span class="menu-chip-name">{{ m.name }}</span>
            <span class="menu-chip-price">{{ formatTHB(m.price) }}</span>
          </button>
        </div>
      </div>
      <small v-if="formErrors.menu" class="p-error">{{ formErrors.menu }}</small>
    </section>

    <!-- Step 3: Amount & Quick Modifiers -->
    <section class="form-section">
      <div class="section-label-row">
        <label class="section-heading">
          <span class="step-num">3</span>
          จำนวนเงินที่จ่าย (บาท) <span class="required">*</span>
        </label>
      </div>

      <div class="amount-entry-box">
        <div class="amount-display-row">
          <span class="currency-symbol">฿</span>
          <InputNumber 
            v-model="amount" 
            :min="0" 
            :max="10000" 
            :step="1"
            class="amount-input"
            inputClass="text-2xl font-bold text-center"
            placeholder="0"
          />
        </div>

        <!-- Quick Modifier Chips for students: พิเศษ, ไข่ดาว, เพิ่มข้าว -->
        <div class="modifiers-row">
          <span class="modifier-hint">กดปรับยอด:</span>
          <button type="button" class="modifier-btn" @click="addModifier(5)">+5 บ.</button>
          <button type="button" class="modifier-btn" @click="addModifier(10)">+10 บ. (พิเศษ/ไข่ดาว)</button>
          <button type="button" class="modifier-btn" @click="addModifier(-5)">-5 บ.</button>
        </div>
      </div>
      <small v-if="formErrors.amount" class="p-error">{{ formErrors.amount }}</small>

      <!-- REAL-TIME BUDGET SIMULATION -->
      <div class="budget-simulator-card" :class="{ 'sim-over': isProjectedOver }">
        <div class="sim-row">
          <span class="sim-label">งบที่เหลือปัจจุบัน:</span>
          <span class="sim-value">{{ formatTHB(currentRemaining) }}</span>
        </div>
        <div class="sim-row">
          <span class="sim-label">หักค่ามื้อนี้:</span>
          <span class="sim-value text-danger">-{{ formatTHB(amount || 0) }}</span>
        </div>
        <div class="sim-divider"></div>
        <div class="sim-row font-bold">
          <span class="sim-label">หลังมื้อนี้จะเหลือ:</span>
          <span class="sim-value" :class="isProjectedOver ? 'text-danger' : 'text-primary'">
            {{ formatTHB(projectedRemaining) }}
          </span>
        </div>
        <div v-if="isProjectedOver" class="sim-warning">
          <i class="pi pi-info-circle"></i>
          <span>มื้อนี้จะเกินงบรายวันไป {{ formatTHB(Math.abs(projectedRemaining)) }} (ไม่เป็นไร ค่อยปรับมื้อหน้า)</span>
        </div>
      </div>
    </section>

    <!-- Step 4: Category & Note (Optional details) -->
    <details class="extra-details-accordion">
      <summary class="accordion-summary">
        <span>ข้อมูลเพิ่มเติม (หมวดหมู่, วันที่, บันทึกช่วยจำ)</span>
        <i class="pi pi-angle-down"></i>
      </summary>
      
      <div class="accordion-content">
        <div class="form-field">
          <label class="text-xs font-semibold text-muted">หมวดหมู่</label>
          <div class="category-chips">
            <button
              v-for="cat in EXPENSE_CATEGORIES"
              :key="cat.value"
              type="button"
              class="cat-chip"
              :class="{ 'cat-active': category === cat.value }"
              @click="category = cat.value as ExpenseCategory"
            >
              {{ cat.label }}
            </button>
          </div>
        </div>

        <div class="form-field mt-3">
          <label class="text-xs font-semibold text-muted">วันที่จ่าย</label>
          <input v-model="date" type="date" class="custom-date-input" />
        </div>

        <div class="form-field mt-3">
          <label class="text-xs font-semibold text-muted">โน้ตช่วยจำ (ถ้ามี)</label>
          <InputText v-model="note" placeholder="เช่น กินกับเพื่อน, จ่ายพร้อมเป๊ปซี่" class="w-full" />
        </div>
      </div>
    </details>

    <!-- STICKY BOTTOM SAVE ACTION BAR FOR MOBILE -->
    <div class="sticky-action-bar">
      <div class="bar-inner">
        <button 
          type="button" 
          class="cancel-btn"
          @click="emit('cancel')"
        >
          ยกเลิก
        </button>
        <button 
          type="submit" 
          class="submit-btn"
          :disabled="!amount || amount <= 0"
        >
          <i class="pi pi-check"></i>
          <span>{{ isEditing ? 'บันทึกการแก้ไข' : `บันทึกรายจ่าย ${amount > 0 ? formatTHB(amount) : ''}` }}</span>
        </button>
      </div>
    </div>
  </form>
</template>

<style scoped>
.quick-expense-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding-bottom: 80px; /* Space for sticky bar */
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.section-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-heading {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.step-num {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--primary-color);
  color: #ffffff;
  font-size: 0.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.required {
  color: var(--warning-coral);
}

.selected-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary-color);
  background: var(--primary-light);
  padding: 0.2rem 0.6rem;
  border-radius: var(--border-radius-full);
}

/* Search bar */
.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: var(--text-light);
  font-size: 0.85rem;
}

.custom-search-input {
  width: 100%;
  padding: 0.65rem 0.75rem 0.65rem 2.2rem;
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius-sm);
  font-family: inherit;
  font-size: 0.85rem;
  background: #ffffff;
  outline: none;
  min-height: 44px;
}

.custom-search-input:focus {
  border-color: var(--primary-color);
}

.clear-btn {
  position: absolute;
  right: 0.75rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0.25rem;
}

/* Chips container */
.chips-container {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding-bottom: 0.25rem;
  -webkit-overflow-scrolling: touch;
}

.chip-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: #ffffff;
  border: 1.5px solid var(--surface-border);
  border-radius: var(--border-radius-full);
  padding: 0.45rem 0.85rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-main);
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.15s ease;
  min-height: 44px;
  font-family: inherit;
}

.chip-item:hover {
  border-color: var(--primary-color);
  background: var(--surface-hover);
}

.chip-selected {
  background: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
  color: #ffffff !important;
  font-weight: 600;
}

/* Menu Grid */
.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 0.6rem;
}

.menu-chip-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: #ffffff;
  border: 1.5px solid var(--surface-border);
  border-radius: var(--border-radius);
  padding: 0.75rem;
  cursor: pointer;
  min-height: 64px;
  text-align: left;
  font-family: inherit;
  transition: all 0.15s ease;
}

.menu-chip-card:hover {
  border-color: var(--primary-color);
  background: var(--surface-hover);
}

.menu-selected {
  border-color: var(--primary-color) !important;
  background: var(--primary-light) !important;
  box-shadow: 0 0 0 1px var(--primary-color);
}

.menu-chip-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-main);
  line-height: 1.25;
}

.menu-chip-price {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-top: 0.35rem;
}

.hint-card {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background: var(--surface-hover);
  padding: 1rem;
  border-radius: var(--border-radius);
  font-size: 0.85rem;
  color: var(--text-muted);
}

/* Amount Box */
.amount-entry-box {
  background: #ffffff;
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.amount-display-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  width: 100%;
  max-width: 240px;
}

.currency-symbol {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--primary-color);
}

.amount-input {
  width: 100%;
}

.modifiers-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  justify-content: center;
}

.modifier-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.modifier-btn {
  background: var(--surface-hover);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius-full);
  padding: 0.25rem 0.6rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-main);
  cursor: pointer;
  min-height: 36px;
  font-family: inherit;
}

.modifier-btn:hover {
  background: var(--primary-light);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

/* Simulator Card */
.budget-simulator-card {
  background: #ffffff;
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  padding: 0.85rem 1rem;
  font-size: 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.sim-over {
  background: #FFF5F5;
  border-color: #FECACA;
}

.sim-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sim-label {
  color: var(--text-muted);
}

.sim-value {
  font-weight: 600;
}

.sim-divider {
  height: 1px;
  background-color: var(--surface-border);
  margin: 0.15rem 0;
}

.sim-warning {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.775rem;
  color: var(--warning-coral);
  margin-top: 0.25rem;
}

/* Accordion */
.extra-details-accordion {
  background: #ffffff;
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  overflow: hidden;
}

.accordion-summary {
  padding: 0.85rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
  min-height: 44px;
}

.accordion-content {
  padding: 0 1rem 1rem;
  border-top: 1px solid var(--surface-border);
}

.category-chips {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
  margin-top: 0.35rem;
}

.cat-chip {
  background: var(--surface-hover);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius-full);
  padding: 0.35rem 0.65rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  min-height: 38px;
}

.cat-active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: #ffffff;
  font-weight: 600;
}

.custom-date-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius-sm);
  font-family: inherit;
  font-size: 0.85rem;
  min-height: 44px;
}

/* Sticky Action Bar */
.sticky-action-bar {
  position: fixed;
  bottom: calc(56px + max(0.4rem, env(safe-area-inset-bottom, 0px)));
  left: 0;
  right: 0;
  z-index: 35;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  border-top: 1px solid var(--surface-border);
  padding: 0.6rem 1rem;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.05);
}

@media (min-width: 768px) {
  .sticky-action-bar {
    position: static;
    background: transparent;
    border: none;
    padding: 1rem 0 0;
    box-shadow: none;
  }
}

.bar-inner {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  gap: 0.75rem;
}

.cancel-btn {
  background: #ffffff;
  border: 1px solid var(--surface-border);
  color: var(--text-muted);
  border-radius: var(--border-radius);
  padding: 0.75rem 1rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  min-height: 48px;
}

.submit-btn {
  flex: 1;
  background: var(--primary-color);
  border: none;
  color: #ffffff;
  border-radius: var(--border-radius);
  padding: 0.75rem 1.25rem;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-family: inherit;
  box-shadow: 0 4px 12px rgba(27, 77, 62, 0.25);
  min-height: 48px;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
