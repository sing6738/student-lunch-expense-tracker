<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
 
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
 
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
 
const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = 'กรอกชื่อผู้ใช้และรหัสผ่านให้ครบก่อนนะ'
    return
  }
 
  loading.value = true
  error.value = ''
 
  try {
    const success = await authStore.login(username.value, password.value)
    if (success) {
      const redirect = (route.query.redirect as string) || '/'
      router.push(redirect)
    } else {
      error.value = authStore.error || 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง ลองใหม่อีกครั้ง'
    }
  } catch (e: any) {
    error.value = e.message || 'เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ ตรวจสอบอินเทอร์เน็ตแล้วลองใหม่'
  } finally {
    loading.value = false
  }
}
</script>
 
<template>
  <main class="login-page">
    <section class="login-card" aria-labelledby="login-title">
      <header class="login-head">
        <div class="login-logo" aria-hidden="true">🍱</div>
        <h1 id="login-title" class="login-title">เข้าสู่ระบบ</h1>
        <p class="login-sub">บันทึกค่าข้าวกลางวัน แล้วดูว่าวันนี้เหลืองบเท่าไร</p>
      </header>
 
      <div class="perforation" aria-hidden="true"></div>
 
      <form class="login-form" novalidate @submit.prevent="handleLogin">
        <div v-if="error" class="login-error" role="alert">
          <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
          <span>{{ error }}</span>
        </div>
 
        <div class="field">
          <label for="username" class="field-label">ชื่อผู้ใช้</label>
          <InputText
            id="username"
            v-model="username"
            class="field-input"
            placeholder="ใส่ชื่อผู้ใช้"
            autocomplete="username"
          />
        </div>
 
        <div class="field">
          <label for="password" class="field-label">รหัสผ่าน</label>
          <Password
            id="password"
            v-model="password"
            :feedback="false"
            toggleMask
            class="field-password"
            inputClass="field-input"
            placeholder="ใส่รหัสผ่าน"
          />
        </div>
 
        <Button
          type="submit"
          :label="loading ? 'กำลังเข้าสู่ระบบ' : 'เข้าสู่ระบบ'"
          :loading="loading"
          :disabled="loading"
          class="submit-btn"
        />
 
        <p class="alt-action">
          ยังไม่มีบัญชี?
          <router-link to="/register" class="alt-link">สมัครสมาชิก</router-link>
        </p>
      </form>
    </section>
  </main>
</template>
 
<style scoped>
.login-page {
  --cream: #f1ebdc;
  --card: #ffffff;
  --ink: #1f2a24;
  --muted: #5d6a62;
  --leaf: #1f6b4a;
  --leaf-dark: #1b4d3e;
  --line: #d9d0ba;
  --coral: #c4452d;
  --coral-bg: #fdeeea;
 
  display: flex;
  align-items: flex-start;
  justify-content: center;
  min-height: 70vh;
  padding: 32px 16px calc(32px + env(safe-area-inset-bottom, 0px));
  background: var(--cream);
  color: var(--ink);
  font-family: 'Sarabun', 'Prompt', system-ui, sans-serif;
}
 
.login-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  overflow: hidden;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: 0 2px 6px rgba(60, 50, 20, 0.08);
}
 
.login-head {
  padding: 28px 24px 22px;
}
 
.login-logo {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  margin-bottom: 14px;
  font-size: 26px;
  background: var(--leaf-dark);
  border-radius: 14px;
}
 
.login-title {
  margin: 0;
  font-family: 'Prompt', 'Sarabun', system-ui, sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.3;
  color: var(--ink);
}
 
.login-sub {
  margin: 6px 0 0;
  font-size: 1rem;
  line-height: 1.6;
  color: var(--muted);
}
 
/* Coupon-style perforation: dashed line with a notch on each side */
.perforation {
  position: relative;
  height: 0;
  border-top: 2px dashed var(--line);
}
.perforation::before,
.perforation::after {
  content: '';
  position: absolute;
  top: -12px;
  width: 22px;
  height: 22px;
  background: var(--cream);
  border: 1px solid var(--line);
  border-radius: 50%;
}
.perforation::before {
  left: -12px;
}
.perforation::after {
  right: -12px;
}
 
.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 24px 24px 28px;
}
 
.login-error {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 12px 14px;
  font-size: 0.95rem;
  line-height: 1.5;
  color: var(--coral);
  background: var(--coral-bg);
  border: 1px solid #f0c4ba;
  border-radius: 12px;
}
.login-error i {
  margin-top: 3px;
}
 
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
 
.field-label {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
}
 
.login-card .field-input,
.login-card :deep(.field-input) {
  width: 100%;
  min-height: 48px;
  padding: 0 14px;
  font: inherit;
  font-size: 1rem;
  color: var(--ink);
  background: #fff;
  border: 1.5px solid var(--line);
  border-radius: 14px;
  box-shadow: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.login-card :deep(.field-input::placeholder),
.login-card .field-input::placeholder {
  color: #8a8570;
}
.login-card .field-input:focus,
.login-card :deep(.field-input:focus) {
  outline: none;
  border-color: var(--leaf);
  box-shadow: 0 0 0 3px rgba(31, 107, 74, 0.25);
}
 
.login-card :deep(.p-password) {
  display: block;
  position: relative;
  width: 100%;
}
.login-card :deep(.p-password .field-input) {
  padding-right: 48px;
}
.login-card :deep(.p-password-toggle-mask-icon),
.login-card :deep(.p-password .p-icon) {
  color: var(--muted);
  cursor: pointer;
}
 
.login-card .submit-btn {
  width: 100%;
  min-height: 48px;
  margin-top: 4px;
  font-family: 'Prompt', 'Sarabun', system-ui, sans-serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: #fff;
  background: var(--leaf);
  border: 1px solid var(--leaf);
  border-radius: 14px;
  transition: background-color 0.15s ease;
}
.login-card .submit-btn:hover:not(:disabled) {
  background: var(--leaf-dark);
  border-color: var(--leaf-dark);
}
.login-card .submit-btn:focus-visible {
  outline: 3px solid rgba(31, 107, 74, 0.4);
  outline-offset: 2px;
}
.login-card .submit-btn:disabled {
  opacity: 0.8;
  cursor: progress;
}
 
.alt-action {
  margin: 4px 0 0;
  text-align: center;
  font-size: 1rem;
  color: var(--muted);
}
.alt-link {
  display: inline-block;
  padding: 10px 4px;
  font-weight: 600;
  color: var(--leaf);
  text-decoration: none;
}
.alt-link:hover,
.alt-link:focus-visible {
  text-decoration: underline;
  text-underline-offset: 3px;
}
.alt-link:focus-visible {
  outline: 3px solid rgba(31, 107, 74, 0.4);
  outline-offset: 2px;
  border-radius: 6px;
}
 
@media (min-width: 640px) {
  .login-page {
    align-items: center;
    padding-top: 48px;
  }
}
 
@media (prefers-reduced-motion: reduce) {
  .login-card .field-input,
  .login-card :deep(.field-input),
  .login-card .submit-btn {
    transition: none;
  }
}
</style>
 