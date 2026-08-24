import { apiClient } from './client'
import type { ApiResponse } from '../types/api'
import type { Restaurant, Menu } from '../types/restaurant'

export const restaurantsApi = {
  list: () => apiClient.get<ApiResponse<Restaurant[]>>('/restaurants'),
  getMenus: (restaurantId: number) => apiClient.get<ApiResponse<Menu[]>>(`/restaurants/${restaurantId}/menus`),
  getMenu: (menuId: number) => apiClient.get<ApiResponse<Menu>>(`/menus/${menuId}`),
}
