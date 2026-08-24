import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { restaurantsApi } from '@/api/restaurants'
import type { Restaurant, Menu } from '@/types/restaurant'

export const useRestaurantsStore = defineStore('restaurants', () => {
  const restaurants = ref<Restaurant[]>([])
  // Cache menus per restaurant_id so switching restaurants in a form
  // doesn't refetch every time.
  const menusByRestaurant = ref<Record<number, Menu[]>>({})
  const loading = ref(false)
  const error = ref<string | null>(null)

  const activeRestaurants = computed(() => restaurants.value.filter(r => r.is_active))

  async function fetchRestaurants() {
    loading.value = true
    error.value = null
    try {
      const res = await restaurantsApi.list()
      restaurants.value = res.data.data
      return restaurants.value
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'โหลดรายชื่อร้านไม่สำเร็จ'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchMenus(restaurantId: number, force = false): Promise<Menu[]> {
    if (!force && menusByRestaurant.value[restaurantId]) {
      return menusByRestaurant.value[restaurantId]
    }
    const res = await restaurantsApi.getMenus(restaurantId)
    menusByRestaurant.value[restaurantId] = res.data.data
    return res.data.data
  }

  return {
    restaurants,
    menusByRestaurant,
    loading,
    error,
    activeRestaurants,
    fetchRestaurants,
    fetchMenus
  }
})
