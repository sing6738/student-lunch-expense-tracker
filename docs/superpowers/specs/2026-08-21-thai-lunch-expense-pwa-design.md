# แผนงานฉบับเต็ม: ทำให้ Lunch Expense Tracker ติดตั้งลง iOS ได้ (PWA)

> อ้างอิงจากโค้ดจริงใน `github.com/sing6738/student-lunch-expense-tracker` (Flask MPA, session-based auth, Jinja2 templates, ไม่มี API/PWA ใดๆ อยู่เลย) เทียบกับ design spec เดิม
>
> **หมายเหตุสำคัญ:** นี่คือ PWA (Add to Home Screen ผ่าน Safari) ไม่ใช่การขึ้น App Store — iOS **ไม่รองรับ** การติดตั้ง PWA ผ่าน App Store ต้องติดตั้งผ่าน Safari → Share → "Add to Home Screen" เท่านั้น ถ้าต้องการขึ้น App Store จริงต้องห่อด้วย Capacitor/Cordova แยกเป็นอีกแผนหนึ่ง (ระบุไว้ท้ายเอกสาร)

---

## Phase 0: Backend — แปลง Route ให้เป็น JSON API (P0 Critical)

โค้ดปัจจุบันทุก route ใน `app.py` (29 routes) render HTML โดยตรง ไม่มี JSON API เลยนอกจาก 2 endpoint (`/api/menus/<id>`, `/api/monthly-budget/setup-check`) ต้องแยก logic ออกจาก template

1. **Auth API:**
   - `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`
   - เปลี่ยนจาก Flask-Login (session) → **JWT + HttpOnly cookie แบบคู่** (session cookie ใช้ได้ปกติบน iOS Safari ตราบใดที่ third-party cookie ไม่ถูกบล็อก — แนะนำให้ backend กับ frontend อยู่ domain เดียวกัน/same-site เพื่อเลี่ยงปัญหา ITP ของ Safari)
2. **Expenses API:** ครอบ logic จาก `/expenses/add`, `/expenses/add-multi`, `/expenses/<id>/edit`, `/expenses/<id>/delete`, `/history`, `/history/export` → เป็น `GET/POST/PUT/DELETE /api/expenses`, `POST /api/expenses/batch` (multi-add), `GET /api/expenses/export`
3. **Restaurant/Menu API:** จาก `/manage-menus`, `/restaurants/*`, `/menus/*` → `GET/POST/PUT/DELETE /api/restaurants`, `/api/menus`
4. **Budget API:** จาก `/budget`, `/monthly-budget`, `/monthly-budget/summary` → `GET/PUT /api/budget`, `GET/PUT /api/monthly-budget`, `GET /api/monthly-budget/summary`
5. **Analytics API:** จาก `/analytics` → `GET /api/analytics/summary|trend|categories|calendar`
6. **Online Orders API:** จาก `/online-orders/*` → `GET/POST/PUT/DELETE /api/orders`, `POST /api/orders/<id>/status`
7. **Profile API:** จาก `/profile` → `GET/PUT /api/profile`
8. ติดตั้ง `flask-cors`, `pyjwt`; ตั้งค่า CORS ให้อนุญาตเฉพาะ origin ของ frontend
9. Response format มาตรฐาน `{success, data, error}` ตามที่ design spec ระบุ (ข้อความ error เป็นภาษาไทย)

## Phase 1: Frontend Scaffold

1. `npm create vite@latest frontend -- --template vue-ts`
2. Install: `vue-router`, `pinia`, `axios`, `primevue`, `@primevue/themes`, `vite-plugin-pwa`, `workbox-window`, `chart.js`, `vue-chartjs`, `vee-validate`, `zod`, `dexie`
3. โครงสร้าง: `src/{api,components,composables,router,stores,styles,types,utils,views}`
4. Flask: เพิ่ม SPA catch-all route เสิร์ฟ `frontend/dist/index.html`, ตั้ง static build output ให้ตรงกับ `static/`

## Phase 2: Core Architecture

1. TypeScript types: Expense, Restaurant, Menu, OnlineOrder, MonthlyBudget, User (ให้ตรงกับ `models.py` จริง — รวม field ที่ design doc เดิมไม่ได้ระบุ เช่น `wishlist_name/price`, `fixed_*` ทั้งหมด)
2. Pinia stores: `auth`, `expenses`, `restaurants`, `budget`, `monthlyBudget` (เพิ่มจาก plan เดิม), `analytics`, `orders`
3. API client modules ครบ 7 ไฟล์ (เพิ่ม `monthlyBudget.ts`, `profile.ts` จากของเดิม)
4. Vue Router + auth guard, route ให้ครบทุกหน้าที่มีอยู่จริงในโค้ด (เพิ่ม `MonthlyBudgetView`, `MonthlyBudgetSummaryView`, `ProfileView`, `ManageMenusView`, `AddMultiExpenseView` — ที่ design doc เดิมไม่มี)

## Phase 3: UI Views & Components

สร้าง view ให้ครบทุกหน้าตามฟีเจอร์จริงในโค้ด (ไม่ใช่แค่ตาม design doc เดิม):
Login, Register, Dashboard, AddExpense, AddMultiExpense, EditExpense, History, Analytics, Budget, MonthlyBudget, MonthlyBudgetSummary, OnlineOrders, ManageMenus, Profile, NotFound

## Phase 4: PWA Config — เจาะจงสำหรับ iOS Safari

**iOS Safari มีข้อจำกัดกว่า Android/Chrome มาก ต้องทำเพิ่มเติมจาก manifest ปกติ:**

1. **Manifest (`vite-plugin-pwa`):** `display: 'standalone'`, `start_url`, icons ครบทุกขนาด — **แต่ iOS ไม่อ่าน manifest icons โดยตรงสำหรับหน้าจอโฮม** ต้องเพิ่ม `<link rel="apple-touch-icon">` แยกใน `index.html` ด้วย (180×180 อย่างน้อย)
2. **Meta tags เฉพาะ iOS ที่ต้องเพิ่มใน `index.html`:**
   ```html
   <meta name="apple-mobile-web-app-capable" content="yes">
   <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
   <meta name="apple-mobile-web-app-title" content="LunchTrack">
   <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
   ```
3. **Splash Screen:** iOS ไม่ auto-generate จาก manifest (ก่อน iOS 17) — ต้องสร้าง `apple-touch-startup-image` แยกตามขนาดจอ (iPhone SE, standard, Pro Max, iPad) ด้วย media query แต่ละภาพ หรือใช้ meta theme-color + background ให้ transition ดูเรียบ
4. **Safe Area:** ใช้ CSS `env(safe-area-inset-top/bottom)` รองรับ notch/Dynamic Island (จำเป็นเพราะ `viewport-fit=cover`)
5. **Install Prompt:** iOS **ไม่มี** `beforeinstallprompt` event (ต่างจาก Android) — ต้องสร้าง custom banner สอนผู้ใช้กด Share → "Add to Home Screen" เอง (ตรวจ user agent เพื่อโชว์คำแนะนำเฉพาะ iOS)
6. **Theme color:** iOS Safari ใช้ `<meta name="theme-color">` จำกัดกว่า Android — ทดสอบสีจริงบนเครื่อง

## Phase 5: Offline Capabilities — ปรับให้เข้ากับข้อจำกัด iOS

1. **Service Worker Strategies:** ตามตารางเดิม (CacheFirst สำหรับ app shell, NetworkFirst สำหรับ API GET)
2. **⚠️ Background Sync API ไม่รองรับบน Safari/iOS ทั้งหมด** — ต้อง fallback: sync คิวตอนแอป foreground (`visibilitychange` event) หรือตอนเปิดแอปใหม่ แทนที่จะพึ่ง SW `sync` event อย่างเดียว
3. **⚠️ Safari มี Intelligent Tracking Prevention (ITP)** ที่ลบข้อมูล IndexedDB/localStorage ของเว็บที่ไม่ถูกเปิดใน Safari นาน 7 วัน — ต้องแจ้งผู้ใช้ให้เปิดแอปเป็นระยะ หรือออกแบบไม่ให้ offline queue ต้องอยู่ได้นานเกินไปโดยไม่ sync
4. **Push Notifications:** ใช้ได้เฉพาะ **iOS 16.4 ขึ้นไป และต้องเพิ่มลงหน้าจอโฮมแล้วเท่านั้น** ต้องขอ permission หลัง user gesture ชัดเจน (ปุ่มกด ไม่ใช่ auto-prompt)
5. **Storage Quota:** Safari จำกัด storage ต่อ origin เข้มกว่า Chrome — ทดสอบ Dexie.js queue กับ cache ไม่ให้เกิน quota

## Phase 6: Thai Localization (เหมือนเดิม)
Buddhist Era date, Baht currency, number formatting

## Phase 7: PWA Assets & Icons

1. สร้างไอคอนครบ: 72/96/128/144/152/192(maskable)/384/512 (Android/manifest) **+ apple-touch-icon 180×180** (iOS เฉพาะ)
2. Service Worker registration ใน `main.ts` ด้วย `workbox-window`
3. Custom "Add to Home Screen" banner สำหรับ iOS (Phase 4 ข้อ 5)
4. Update detection + toast แจ้งเวอร์ชันใหม่

## Phase 8: Deployment — HTTPS จำเป็นสำหรับ iOS PWA

1. PWA **ต้องรันบน HTTPS เท่านั้น** — Service Worker จะไม่ทำงานบน HTTP (ยกเว้น localhost ตอน dev) ตรวจสอบ Render deployment ใช้ HTTPS อยู่แล้ว (Render ให้ TLS อัตโนมัติ)
2. ตรวจสอบ CORS/cookie settings ให้ frontend-backend อยู่ domain เดียวกันหรือ subdomain เดียวกัน เพื่อเลี่ยงปัญหา Safari บล็อก third-party cookie
3. Database migration (Render → Neon ตามที่คุยไว้ก่อนหน้า) ให้เสร็จก่อน deploy เวอร์ชัน PWA

## Phase 9: Testing บน iOS จริง

**ข้อควรระวัง:** Chrome DevTools จำลอง iOS ไม่แม่นยำ ต้องทดสอบบนอุปกรณ์จริงหรือ Safari บน macOS + iOS Simulator (Xcode)

1. ทดสอบ Add to Home Screen บน iPhone จริง (ไอคอน, splash, standalone mode ไม่มี Safari UI)
2. ทดสอบ offline read/write + sync หลังกลับมา online
3. ทดสอบ safe-area บนเครื่องมี notch/Dynamic Island
4. Lighthouse audit (PWA ≥ 90, Performance ≥ 80) — หมายเหตุ: Lighthouse PWA score ไม่ได้ครอบคลุมข้อจำกัดเฉพาะ iOS ทั้งหมด ต้องเช็คด้วยมือตามข้อ 1-3
5. ทดสอบ push notification (ถ้าทำ) บน iOS 16.4+ หลัง add to home screen แล้วเท่านั้น

---

## ⚠️ ถ้าต้องการขึ้น App Store จริง (ไม่ใช่แค่ PWA)

ถ้าเป้าหมายคือให้ดาวน์โหลดจาก App Store ได้ (ไม่ใช่แค่ Add to Home Screen ผ่าน Safari) ต้องทำเพิ่มอีกชุดหนึ่งซึ่งไม่ใช่ PWA แล้ว:
- ห่อ frontend ด้วย **Capacitor** (แนะนำ เพราะ Vue/Vite รองรับดี) หรือ Cordova
- ต้องมี Apple Developer account ($99/ปี), เครื่อง Mac + Xcode สำหรับ build/submit
- ปรับ UI ให้ผ่าน App Store Review Guidelines (ไม่ใช่แค่ web wrapper เปล่าๆ Apple อาจปฏิเสธถ้าดูเป็นแค่เว็บ)
- Push notification จะใช้ APNs โดยตรงแทน Web Push

ถ้าสนใจแนวทางนี้ บอกได้ครับ จะแยกทำเป็นแผนเพิ่มเติม

---

## สรุป Priority

| Priority | งาน |
|---|---|
| P0 | Backend → JSON API (Phase 0) — ทุกอย่างต่อจากนี้พึ่งพา phase นี้ |
| P0 | Frontend scaffold + stores + views ครบตามฟีเจอร์จริง (Phase 1-3) |
| P1 | PWA config เฉพาะ iOS: apple-touch-icon, meta tags, splash, custom install banner (Phase 4, 7) |
| P1 | Offline queue พร้อม fallback (ไม่พึ่ง Background Sync API อย่างเดียว) (Phase 5) |
| P2 | Deployment HTTPS/CORS check (Phase 8) |
| P2 | Testing บนอุปกรณ์ iOS จริง (Phase 9) |