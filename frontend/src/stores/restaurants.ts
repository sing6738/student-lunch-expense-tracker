import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Restaurant, Menu } from '@/types/restaurant'

export const useRestaurantsStore = defineStore('restaurants', () => {
  const restaurants = ref<Restaurant[]>([])
  
  const activeRestaurants = computed(() => restaurants.value.filter(r => r.is_active))

  // Mock fetch for now, will connect to API in Task 5
  async function fetchRestaurants() {
    // TODO: implement API call
    restaurants.value = []
  }

  async function fetchMenus(restaurantId: number): Promise<Menu[]> {
    // TODO: implement API call
    return []
  }

  return {
    restaurants,
    activeRestaurants,
    fetchRestaurants,
    fetchMenus
  }
})
