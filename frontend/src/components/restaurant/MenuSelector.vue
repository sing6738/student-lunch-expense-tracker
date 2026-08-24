<script setup lang="ts">
import { ref, watch } from 'vue'
import { useField } from 'vee-validate'
import { useRestaurantsStore } from '@/stores/restaurants'
import type { Menu } from '@/types/restaurant'
import Select from 'primevue/select'
import { formatTHB } from '@/utils/currency'

interface Props {
  modelValue: number | null
  restaurantId: number | null
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: number | null]
  change: [value: number | null]
}>()

const restaurantsStore = useRestaurantsStore()
const { value: field, errorMessage } = useField<number>('menu_id')

const menus = ref<Menu[]>([])
const loading = ref(false)

watch(() => props.restaurantId, async (restaurantId) => {
  if (restaurantId) {
    loading.value = true
    menus.value = await restaurantsStore.fetchMenus(restaurantId)
    loading.value = false
  } else {
    menus.value = []
  }
  
  if (props.modelValue && !menus.value.find(m => m.id === props.modelValue)) {
    emit('update:modelValue', null)
    emit('change', null)
  }
}, { immediate: true })

function handleSelect(menuId: number): void {
  emit('update:modelValue', menuId)
  emit('change', menuId)
}

function clearSelection(): void {
  emit('update:modelValue', null)
  emit('change', null)
}
</script>

<template>
  <div class="menu-selector">
    <label class="p-inputwrapper">
      <Select
        v-model="field"
        :options="menus"
        optionLabel="name"
        optionValue="id"
        :optionDisabled="menu => !menu.is_active"
        placeholder="เลือกเมนู"
        :disabled="props.disabled || loading || !props.restaurantId"
        :filter="true"
        filterBy="name"
        :showClear="!props.disabled"
        :loading="loading"
        @change="handleSelect($event.value)"
        @clear="clearSelection"
        class="p-fluid"
      >
        <template #option="{ option }">
          <div class="menu-option">
            <span class="menu-name">{{ option.name }}</span>
            <span class="menu-price">{{ formatTHB(option.price) }}</span>
          </div>
        </template>
      </Select>
      <small v-if="errorMessage.value" class="p-error">{{ errorMessage }}</small>
      <small v-if="!props.restaurantId" class="p-hint">กรุณาเลือกร้านอาหารก่อน</small>
    </label>
  </div>
</template>

<style scoped>
.menu-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.menu-price {
  color: var(--primary-color);
  font-weight: 600;
  margin-left: 1rem;
}
.p-hint {
  color: #888;
  font-size: 0.8rem;
}
</style>
