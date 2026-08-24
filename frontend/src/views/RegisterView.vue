<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')

const handleRegister = async () => {
  if (!username.value || !email.value || !password.value) {
    error.value = 'กรุณากรอกข้อมูลให้ครบถ้วน'
    return
  }
  
  if (password.value !== confirmPassword.value) {
    error.value = 'รหัสผ่านไม่ตรงกัน'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const success = await authStore.register({ 
      username: username.value, 
      email: email.value, 
      password: password.value 
    })
    
    if (success) {
      router.push({ name: 'login', query: { registered: 'true' } })
    } else {
      error.value = authStore.error || 'สมัครสมาชิกไม่สำเร็จ'
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
        <h1 class="text-2xl font-bold text-primary">สมัครสมาชิก</h1>
        <p class="text-gray-500 mt-2">Lunch Expense Tracker</p>
      </div>
      
      <Message v-if="error" severity="error" :closable="false" class="mb-4">{{ error }}</Message>
      
      <form @submit.prevent="handleRegister" class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <label for="username">ชื่อผู้ใช้</label>
          <InputText id="username" v-model="username" />
        </div>
        
        <div class="flex flex-col gap-2">
          <label for="email">อีเมล</label>
          <InputText id="email" type="email" v-model="email" />
        </div>
        
        <div class="flex flex-col gap-2">
          <label for="password">รหัสผ่าน</label>
          <Password id="password" v-model="password" toggleMask />
        </div>
        
        <div class="flex flex-col gap-2">
          <label for="confirmPassword">ยืนยันรหัสผ่าน</label>
          <Password id="confirmPassword" v-model="confirmPassword" :feedback="false" toggleMask />
        </div>
        
        <Button type="submit" label="สมัครสมาชิก" :loading="loading" class="mt-4" />
      </form>
      
      <div class="text-center mt-6 text-sm">
        มีบัญชีอยู่แล้ว? 
        <router-link to="/login" class="text-primary font-semibold hover:underline">เข้าสู่ระบบ</router-link>
      </div>
    </div>
  </div>
</template>
