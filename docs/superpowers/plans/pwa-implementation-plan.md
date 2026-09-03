# PWA Implementation Plan

## Phase 1: Foundation (Scaffolding & Config)
1. **Scaffold Frontend:** 
   - Run `npm create vite@latest frontend -- --template vue-ts`
   - Install dependencies: `vue-router`, `pinia`, `axios`, `primevue`, `@primevue/themes`, `vite-plugin-pwa`, `workbox-window`, `chart.js`, `vue-chartjs`
2. **Project Structure:**
   - Create directories: `src/api`, `src/components`, `src/composables`, `src/router`, `src/stores`, `src/styles`, `src/types`, `src/utils`, `src/views`
3. **Vite & PWA Configuration:**
   - Configure `vite.config.ts` for PrimeVue and VitePWA (Manifest, Workbox strategies).
4. **Backend Setup:**
   - Update `app.py` to serve SPA catch-all route.
   - Install `flask-cors` and `pyjwt`. Update `config.py` for CORS.

## Phase 2: Core Architecture (Stores & Routing)
1. **Types & Utils:**
   - Define TypeScript interfaces for API responses, Expense, Restaurant, Budget.
   - Implement `useFormat` (Thai dates, Baht, numbers).
2. **State Management (Pinia):**
   - Create `auth`, `expenses`, `restaurants`, `budget`, `analytics` stores.
3. **Routing:**
   - Set up Vue Router with navigation guards (auth requirements).
4. **API Client & Auth:**
   - Configure Axios instance with interceptors for token management.
   - Implement `useAuth()` composable.

## Phase 3: UI Components & Views
1. **PrimeVue Setup:**
   - Initialize PrimeVue in `main.ts` with Aura/Lara theme and Thai primary color (#2E7D32).
2. **Layouts & Shared UI:**
   - Create `App.vue` layout (Header, Footer/Sidebar navigation).
3. **Authentication Views:**
   - `LoginView` and `RegisterView` components.
4. **Main Application Views:**
   - `DashboardView`, `HistoryView`, `BudgetView`, `AnalyticsView`, `AddExpenseView`, `SettingsView`.

## Phase 4: Offline Capabilities & Polish
1. **Offline Queuing:**
   - Setup IndexedDB (Dexie.js) for offline expense creation.
   - Implement background sync logic in Service Worker and `useOffline` composable.
2. **PWA UX:**
   - Add install prompts and update detection notifications.
3. **Testing & Performance:**
   - Run Lighthouse audits.
   - Fix any responsive design issues.
