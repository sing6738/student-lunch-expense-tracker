import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ordersApi } from '@/api/orders'
import type { OnlineOrder, OnlineOrderFormData } from '@/types/order'

export const useOrdersStore = defineStore('orders', () => {
  const orders = ref<OnlineOrder[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchOrders() {
    loading.value = true
    error.value = null
    try {
      const res = await ordersApi.list()
      orders.value = res.data.data
      return orders.value
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'โหลดรายการสั่งซื้อไม่สำเร็จ'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function addOrder(data: OnlineOrderFormData) {
    const res = await ordersApi.create(data)
    return res.data.data?.id
  }

  async function updateOrder(id: number, data: Partial<OnlineOrderFormData>) {
    const res = await ordersApi.update(id, data)
    return res.data.data
  }

  // There's no dedicated /orders/:id/status route — status is just one
  // of the fields the PUT /orders/:id endpoint accepts, so this is a thin
  // convenience wrapper rather than a separate API call.
  async function updateStatus(id: number, status: string) {
    return updateOrder(id, { status })
  }

  async function deleteOrder(id: number) {
    await ordersApi.delete(id)
    orders.value = orders.value.filter(o => o.id !== id)
  }

  return {
    orders,
    loading,
    error,
    fetchOrders,
    addOrder,
    updateOrder,
    updateStatus,
    deleteOrder
  }
})
