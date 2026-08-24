# PWA Implementation Progress (iOS Focus)

## Phase 0: Backend API (P0 Critical)
- [x] Auth API (register, login, logout, me)
- [x] Expenses API (CRUD, export)
- [x] Expenses API (batch multi-add) - **NEW**
- [x] Restaurant/Menu API
- [x] Budget API (daily)
- [x] Monthly Budget API (setup, summary, update) - **NEW**
- [x] Analytics API
- [x] Online Orders API
- [x] Profile API - **NEW**
- [x] CORS Config / JWT

## Phase 1: Frontend Scaffold
- [x] Vite + Vue TS + Dependencies
- [x] Project Structure
- [x] Vite & PWA Config (Basic)
- [x] Backend Serving (Catch-all route)

## Phase 2: Core Architecture
- [x] TypeScript Types (Expense, Restaurant, Budget, Analytics, Order)
- [x] TypeScript Types (MonthlyBudget, User expanded) - **NEW**
- [x] API Client Modules (auth, expenses, restaurants, budget, analytics, orders)
- [x] API Client Modules (monthlyBudget, profile) - **NEW**
- [ ] Pinia Stores (auth, expenses, restaurants, budget, analytics, orders)
- [ ] Pinia Stores (monthlyBudget, profile) - **NEW**
- [ ] Vue Router setup (guards, routes)

## Phase 3: UI Views & Components
- [ ] Login / Register
- [ ] Dashboard
- [ ] AddExpense / AddMultiExpense / EditExpense
- [ ] History / Analytics
- [ ] Budget / MonthlyBudget / MonthlyBudgetSummary
- [ ] OnlineOrders / ManageMenus / Profile
- [ ] NotFound

## Phase 4: PWA Config (iOS Specific)
- [ ] apple-touch-icon in index.html
- [ ] iOS Meta tags (apple-mobile-web-app-capable, status-bar-style, title)
- [ ] Splash Screen handling
- [ ] Safe Area (env safe-area-inset)
- [ ] Custom Install Banner for iOS
- [ ] Theme color test

## Phase 5: Offline Capabilities
- [ ] SW Strategies (CacheFirst, NetworkFirst)
- [ ] Dexie.js Queue
- [ ] Fallback sync for iOS (visibilitychange / app open)
- [ ] Quota / ITP checks

## Phase 6 & 7: Localization & Assets
- [ ] THB format, Buddhist Era, Number formatting
- [ ] Icons (72-512 + 180x180 iOS)
- [ ] SW Registration in main.ts
- [ ] Update detection + Toast

## Phase 8 & 9: Deployment & Testing
- [ ] HTTPS / CORS validation
- [ ] Testing on iOS Simulator / Real device
