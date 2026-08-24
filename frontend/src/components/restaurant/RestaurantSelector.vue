<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useField } from 'vee-validate'
import { useRestaurantsStore } from '@/stores/restaurants'
import type { Restaurant } from '@/types/restaurant'
import Select from 'primevue/select'

interface Props {
  modelValue: number | null
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
const { value: field, errorMessage } = useField<number>('restaurant_id')

const selectedRestaurant = ref<Restaurant | null>(null)

onMounted(() => {
  restaurantsStore.fetchRestaurants()
})

watch(() => props.modelValue, (val) => {
  if (val) {
    selectedRestaurant.value = restaurantsStore.activeRestaurants.find(r => r.id === val) || null
  } else {
    selectedRestaurant.value = null
  }
})

function handleSelect(restaurant: Restaurant): void {
  emit('update:modelValue', restaurant.id)
  emit('change', restaurant.id)
}

function clearSelection(): void {
  emit('update:modelValue', null)
  emit('change', null)
}
</script>

<template>
  <div class="restaurant-selector">
    <label class="p-inputwrapper">
      <Select
        v-model="field"
        :options="restaurantsStore.activeRestaurants"
        optionLabel="name"
        optionValue="id"
        placeholder="เลือกร้านอาหาร"
        :disabled="props.disabled"
        :filter="true"
        filterBy="name"
        :showClear="!props.disabled"
        @change="handleSelect($event.value)"
        @clear="clearSelection"
        class="p-fluid"
      />
      <small v-if="errorMessage.value" class="p-error">{{ errorMessage }}</small>
    </label>
  </div>
</template>

<style scoped>
.restaurant-selector :deep(.p-dropdown) {
  width: 100%;
}
</style>
