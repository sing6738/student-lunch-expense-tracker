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
    const success = await authStore.login(username.value, password.value)
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
  <div class="flex items-center justify-center min-h-screen bg-[#FAF8F5] p-4">
    <div class="w-full max-w-md p-6 bg-white rounded-2xl shadow-sm border border-stone-200/80">
      <div class="text-center mb-6">
        <div class="w-12 h-12 mx-auto mb-3 rounded-2xl bg-emerald-800 text-amber-300 flex items-center justify-center text-2xl font-bold shadow-sm">
          🍱
        </div>
        <h1 class="text-2xl font-bold text-emerald-950">เข้าสู่ระบบ</h1>
        <p class="text-stone-500 mt-1 text-sm">เพื่อนคู่ใจมื้อเที่ยงของเด็ก ม.ปลาย</p>
      </div>

      <Message v-if="error" severity="error" class="mb-4" :closable="false">{{ error }}</Message>

      <form @submit.prevent="handleLogin" class="flex flex-col gap-4">
        <div class="flex flex-col gap-1">
          <label for="username" class="text-sm font-medium text-stone-700">ชื่อผู้ใช้</label>
          <InputText id="username" v-model="username" class="w-full" placeholder="ใส่ชื่อผู้ใช้" />
        </div>

        <div class="flex flex-col gap-1">
          <label for="password" class="text-sm font-medium text-stone-700">รหัสผ่าน</label>
          <Password id="password" v-model="password" :feedback="false" toggleMask class="w-full" inputClass="w-full" placeholder="ใส่รหัสผ่าน" />
        </div>

        <Button type="submit" label="เข้าสู่ระบบ" :loading="loading" class="w-full mt-2" style="background-color: #1B4D3E; border-color: #1B4D3E;" />

        <div class="text-center mt-4 text-sm text-stone-500">
          ยังไม่มีบัญชี? 
          <router-link to="/register" class="text-emerald-800 font-semibold hover:underline">สมัครสมาชิก</router-link>
        </div>
      </form>
    </div>
  </div>
</template>
