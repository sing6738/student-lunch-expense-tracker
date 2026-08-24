<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = 'กรุณากรอกข้อมูลให้ครบถ้วน'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const success = await authStore.login({ username: username.value, password: password.value })
    if (success) {
      const redirect = route.query.redirect as string || '/'
      router.push(redirect)
    } else {
      error.value = authStore.error || 'เข้าสู่ระบบไม่สำเร็จ'
    }
  } catch (e: any) {
    error.value = e.message || 'เกิดข้อผิดพลาดในการเชื่อมต่อ'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-50">
    <div class="w-full max-w-md p-6 bg-white rounded-xl shadow-md">
      <div class="text-center mb-6">
        <h1 class="text-2xl font-bold text-primary">เข้าสู่ระบบ</h1>
        <p class="text-gray-500 mt-2">Lunch Expense Tracker</p>
      </div>
      
      <Message v-if="error" severity="error" :closable="false" class="mb-4">{{ error }}</Message>
      
      <form @submit.prevent="handleLogin" class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <label for="username">ชื่อผู้ใช้</label>
          <InputText id="username" v-model="username" />
        </div>
        
        <div class="flex flex-col gap-2">
          <label for="password">รหัสผ่าน</label>
          <Password id="password" v-model="password" :feedback="false" toggleMask />
        </div>
        
        <Button type="submit" label="เข้าสู่ระบบ" :loading="loading" class="mt-4" />
      </form>
      
      <div class="text-center mt-6 text-sm">
        ยังไม่มีบัญชีใช่หรือไม่? 
        <router-link to="/register" class="text-primary font-semibold hover:underline">สมัครสมาชิก</router-link>
      </div>
    </div>
  </div>
</template>
