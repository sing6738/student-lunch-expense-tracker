# Thai Lunch Expense Tracker - PWA Design Specification

**Date:** 2026-08-21  
**Version:** 1.0  
**Status:** Draft for Review

---

## 1. Executive Summary

Transform the existing Flask-based Thai lunch expense tracking web application into a **Progressive Web App (PWA)** with a modern **Vue 3 + Vite + TypeScript + PrimeVue** frontend, using a **Monorepo architecture** where the frontend builds into Flask's static folder for production deployment.

### Key Goals
- ✅ Installable on iOS/Android (Add to Home Screen)
- ✅ Offline-first: read cached data, write queued for background sync
- ✅ Thai-first UX: Buddhist Era dates, Baht currency, Thai language
- ✅ Responsive: mobile-first, works on iPhone SE to desktop
- ✅ Performance: Lighthouse PWA ≥ 90, Performance ≥ 80

---

## 2. Architecture Overview

### 2.1 Monorepo Structure

```
lunch_expense_app/
├── app.py                    # Flask app factory + API Blueprint + SPA catch-all
├── models.py                 # SQLAlchemy models (unchanged)
├── forms.py                  # Flask-WTF forms (API validation only)
├── config.py                 # Config + CORS settings
├── requirements.txt          # + flask-cors
├── gunicorn.conf.py          # Production config
├── frontend/                 # Vue 3 + Vite + TypeScript project
│   ├── package.json
│   ├── vite.config.ts        # Vite + PWA (Workbox) + PrimeVue config
│   ├── tsconfig.json
│   ├── index.html
│   ├── public/               # Icons, manifest, robots.txt
│   │   ├── manifest.json
│   │   └── icons/
│   └── src/
│       ├── main.ts           # Bootstrap: Vue, Pinia, Router, PrimeVue, i18n
│       ├── App.vue           # Root layout (Header, RouterView, Footer)
│       ├── router/           # Vue Router + Auth guards
│       ├── stores/           # Pinia stores (auth, expenses, restaurants, budget, analytics)
│       ├── api/              # Axios client + endpoint modules
│       ├── components/       # Shared UI components (layout, expense, restaurant, budget, analytics, common)
│       ├── views/            # Page components (Login, Register, Dashboard, AddExpense, EditExpense, History, Analytics, Budget, Settings, NotFound)
│       ├── composables/      # Vue composables (useAuth, useExpenses, useBudget, useOffline, useFormat, usePWA)
│       ├── utils/            # Helpers (date, currency, validation, constants)
│       ├── types/            # TypeScript interfaces (API, Expense, Restaurant, Budget, Analytics)
│       └── styles/           # Global SCSS, PrimeVue theme overrides
├── static/                   # Flask static (served in prod) — Vite build output copied here
└── templates/
    └── index.html            # Catch-all for SPA (serves frontend/dist/index.html)
```

### 2.2 Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   VIEW      │────►│  COMPOSABLE │────►│   STORE     │────►│    API      │
│  (Vue)      │     │  (Logic)    │     │  (Pinia)    │     │  (Axios)    │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                     │
                              ▲                                      │
                              │         ┌─────────────┐              │
                              └────────►│  SERVICE    │◄─────────────┘
                                        │  WORKER     │
                                        │ (Cache+Sync)│
                                        └─────────────┘
```

---

## 3. Technology Stack

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| **Frontend Framework** | Vue 3 | 3.4+ | Composition API, great DX, lightweight |
| **Build Tool** | Vite | 5+ | Fast HMR, PWA plugin, TypeScript native |
| **Language** | TypeScript | 5+ | Type safety, better refactoring |
| **UI Library** | PrimeVue | 4+ | Production-ready components (DataTable, Calendar, Chart, Toast), theming |
| **State Management** | Pinia | 2+ | Vue-native, TypeScript-friendly, devtools |
| **Routing** | Vue Router | 4+ | SPA navigation, guards, lazy loading |
| **HTTP Client** | Axios | 1.7+ | Interceptors, request/response handling |
| **Validation** | VeeValidate + Zod | 4+ / 3+ | Form validation, schema-based |
| **Charts** | Chart.js + vue-chartjs | 4+ / 5+ | Responsive charts for analytics |
| **PWA** | vite-plugin-pwa (Workbox) | 0.19+ | Auto SW generation, offline, background sync |
| **Date/Number** | Intl API (native) | — | Thai locale (th-TH-u-ca-buddhist), no deps |
| **Backend** | Flask | 3+ | Existing, stable |
| **Database** | SQLAlchemy + SQLite/PostgreSQL | 2+ | Existing |
| **Auth** | Session + JWT (dual) | — | HttpOnly cookie + localStorage fallback |

---

## 4. PWA Configuration

### 4.1 Manifest (vite.config.ts → VitePWA)

```typescript
manifest: {
  name: 'Lunch Expense Tracker',
  short_name: 'LunchTrack',
  description: 'ติดตามค่าอาหารกลางวันรายวัน สำหรับนักเรียนไทย',
  theme_color: '#2E7D32',
  background_color: '#F1F8E9',
  display: 'standalone',
  orientation: 'portrait-primary',
  scope: '/',
  start_url: '/',
  icons: [/* 72, 96, 128, 144, 152, 192(maskable), 384, 512(maskable) */],
  categories: ['finance', 'productivity', 'education'],
  lang: 'th-TH',
  dir: 'ltr',
}
```

### 4.2 Service Worker Strategies (Workbox)

| Resource Pattern | Strategy | Cache Name | Expiration |
|------------------|----------|------------|------------|
| App Shell (JS/CSS/HTML) | `CacheFirst` (precache) | `precache-manifest` | N/A (versioned) |
| API GET (`/api/*`) | `NetworkFirst` | `api-cache` | 24h, max 100 entries |
| Static Assets (`/static/*`) | `CacheFirst` | `static-assets` | 30d, max 50 entries |
| Navigation (`/*`) | `NetworkFirst` → fallback `index.html` | — | — |
| API POST/PUT/DELETE | `NetworkOnly` + Background Sync | — | Queued in IndexedDB |

### 4.3 Offline Capabilities

1. **Offline Read**: Cached API responses serve dashboard, history, budget views
2. **Offline Write**: Expense creation queued to IndexedDB (Dexie.js)
3. **Background Sync**: On `online` event or SW `sync` event, process queue sequentially
4. **Install Prompt**: Custom `beforeinstallprompt` handler with PrimeVue Toast

---

## 5. API Specification

### 5.1 Endpoint Structure

All API routes under `/api/` prefix, JSON only.

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login, returns token + sets HttpOnly cookie |
| POST | `/api/auth/register` | Register new user |
| GET | `/api/auth/me` | Get current user (validate session) |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Clear session |

#### Expenses
| Method | Endpoint | Query Params |
|--------|----------|--------------|
| GET | `/api/expenses` | `page`, `per_page`, `date_from`, `date_to`, `category`, `restaurant_id` |
| POST | `/api/expenses` | Body: ExpenseFormData |
| GET | `/api/expenses/:id` | — |
| PUT | `/api/expenses/:id` | Body: ExpenseFormData |
| DELETE | `/api/expenses/:id` | — |
| GET | `/api/expenses/export` | Same as list → CSV |

#### Restaurants & Menus
| Method | Endpoint |
|--------|----------|
| GET | `/api/restaurants` |
| GET | `/api/restaurants/:id/menus` |
| GET | `/api/menus/:id` |

#### Budget
| Method | Endpoint |
|--------|----------|
| GET | `/api/budget` |
| PUT | `/api/budget` |

#### Analytics
| Method | Endpoint |
|--------|----------|
| GET | `/api/analytics/summary` |
| GET | `/api/analytics/trend` |
| GET | `/api/analytics/categories` |
| GET | `/api/analytics/calendar` |

#### Online Orders
| Method | Endpoint |
|--------|----------|
| GET | `/api/orders` |
| POST | `/api/orders` |
| PUT | `/api/orders/:id` |
| DELETE | `/api/orders/:id` |

### 5.2 Response Format

```typescript
// Success
interface ApiResponse<T> {
  success: true;
  data: T;
  meta?: { page: number; per_page: number; total: number };
}

// Error
interface ApiError {
  success: false;
  error: {
    code: string;        // 'VALIDATION_ERROR', 'UNAUTHORIZED', 'NOT_FOUND', 'SERVER_ERROR'
    message: string;     // Thai message for user display
    details?: Record<string, string[]>;
  };
}
```

---

## 6. Frontend Architecture Details

### 6.1 Pinia Stores

| Store | Responsibility |
|-------|----------------|
| `auth` | User profile, token, login/logout/register, session validation |
| `expenses` | List, filters, pagination, CRUD actions, offline queue |
| `restaurants` | Restaurant list, menu cache (by restaurant_id) |
| `budget` | Daily budget, monthly budget (income, fixed expenses, savings) |
| `analytics` | Chart data, summaries, calendar heatmap data |

### 6.2 Key Composables

| Composable | Purpose |
|------------|---------|
| `useAuth()` | Login, logout, register, token management, auth state |
| `useExpenses()` | Fetch, create, update, delete, export, offline queue |
| `useBudget()` | Fetch/update budget settings, calculate progress |
| `useOffline()` | IndexedDB queue (Dexie), sync logic, online/offline detection |
| `useFormat()` | `formatTHB`, `formatDateTH`, `formatNumberTH`, `toBE`, `fromBE` |
| `usePWA()` | Install prompt, update detection, registration |

### 6.3 Views & Routes

| Route | View | Auth | Description |
|-------|------|------|-------------|
| `/login` | `LoginView` | Guest | Login form |
| `/register` | `RegisterView` | Guest | Registration form |
| `/` | `DashboardView` | Auth | Today's expenses, quick add, budget progress, 7-day chart |
| `/expense/new` | `AddExpenseView` | Auth | Restaurant → Menu → Price → Date → Category |
| `/expense/:id/edit` | `EditExpenseView` | Auth | Edit existing expense |
| `/history` | `HistoryView` | Auth | Paginated table, filters, CSV export |
| `/analytics` | `AnalyticsView` | Auth | Charts: trend, categories, calendar heatmap |
| `/budget` | `BudgetView` | Auth | Daily/Monthly settings, progress bars |
| `/settings` | `SettingsView` | Auth | Profile, change password, PWA info |
| `/:pathMatch(.*)*` | `NotFoundView` | Any | 404 page |

### 6.4 Component Library (PrimeVue)

**Used Components:**
- `DataTable` — History, expense list with sorting/filtering/pagination
- `Calendar` — Date picker (Thai Buddhist Era support via `yearNavigator`, `monthNavigator`)
- `Chart` — Line (trend), Doughnut (categories), custom Calendar heatmap
- `Toast` — Success/error/info notifications
- `ConfirmDialog` — Delete confirmations
- `Dialog` / `Sidebar` — Mobile navigation, expense form modal
- `InputNumber` — Price input with Thai Baht formatting
- `Select` / `AutoComplete` — Restaurant/Menu selection
- `ProgressBar` / `ProgressSpinner` — Budget progress, loading states
- `Tabs` / `TabPanel` — Budget daily/monthly tabs
- `Accordion` — Expense categories breakdown
- `Badge` — Status indicators (online orders)
- `Menu` / `Breadcrumb` — Navigation

**Theme:** Custom `Aura` or `Lara` theme with Thai green (`#2E7D32`) primary color.

---

## 7. Thai Localization (i18n)

### 7.1 Date Formatting (Buddhist Era)
```typescript
// Uses Intl.DateTimeFormat with 'th-TH-u-ca-buddhist'
formatDateTH(new Date('2026-08-21'))  // "21 สิงหาคม 2569"
formatDateShortTH(new Date('2026-08-21')) // "21 ส.ค. 2569"
```

### 7.2 Currency Formatting
```typescript
formatTHB(1234)      // "฿1,234"
formatTHB(45.50)     // "฿46" (minimumFractionDigits: 0)
```

### 7.3 Number Formatting
```typescript
formatNumberTH(1234567)  // "1,234,567"
```

### 7.4 Constants (Thai Labels)

```typescript
EXPENSE_CATEGORIES = [
  { value: 'rice', label: 'ข้าว/อาหารจานเดียว', icon: 'pi pi-bowl-rice' },
  { value: 'noodle', label: 'ก๋วยเตี๋ยว/เส้น', icon: 'pi pi-bowl-chopsticks' },
  { value: 'snack', label: 'ของว่าง/ขนม', icon: 'pi pi-cookie' },
  { value: 'drink', label: 'เครื่องดื่ม', icon: 'pi pi-coffee' },
  { value: 'fruit', label: 'ผลไม้', icon: 'pi pi-apple' },
  { value: 'other', label: 'อื่นๆ', icon: 'pi pi-tag' },
]

ORDER_STATUSES = [
  { value: 'ordered', label: 'สั่งแล้ว', color: 'warn' },
  { value: 'shipping', label: 'กำลังส่ง', color: 'info' },
  { value: 'delivered', label: 'ส่งถึงแล้ว', color: 'success' },
  { value: 'cancelled', label: 'ยกเลิก', color: 'danger' },
]
```

---

## 8. Backend Changes (Flask)

### 8.1 New Files/Changes

| File | Change Type | Description |
|------|-------------|-------------|
| `app.py` | **Edit** | Add `api` Blueprint (`/api/*`), JWT/session auth, catch-all SPA route |
| `config.py` | **Edit** | Add `CORS_ORIGINS`, `JWT_SECRET_KEY`, `JWT_EXPIRY_HOURS` |
| `requirements.txt` | **Edit** | Add `flask-cors`, `pyjwt` |
| `forms.py` | **Edit** | Add API validation forms (or use marshmallow/pydantic) |

### 8.2 Auth Strategy
- **Primary**: HttpOnly Secure Cookie (CSRF protected via Flask-WTF)
- **Fallback**: localStorage + Authorization Header (for PWA offline queue)
- **Token**: JWT with 24h expiry, refresh token 30d

### 8.3 CORS Config (Development)
```python
# config.py
CORS_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']
```

---

## 9. Build & Deployment

### 9.1 Development

```bash
# Terminal 1: Flask API
cd lunch_expense_app
.venv\Scripts\activate
flask --app app run --debug --port 5000

# Terminal 2: Vite Dev Server
cd lunch_expense_app/frontend
npm install
npm run dev        # http://localhost:5173, proxies /api to :5000
```

### 9.2 Production Build

```bash
# Build frontend → outputs to ../static/
cd frontend
npm run build

# Flask serves static + SPA catch-all
gunicorn --config gunicorn.conf.py app:create_app
```

### 9.3 Flask Catch-all Route (app.py)
```python
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')
```

---

## 10. Acceptance Criteria (Definition of Done)

| ID | Feature | Criteria |
|----|---------|----------|
| **PWA-1** | Installable | Chrome/Safari shows "Add to Home Screen"; icon appears on iOS/Android home screen |
| **PWA-2** | Offline Read | Open app offline → Dashboard, History, Budget load from cache |
| **PWA-3** | Offline Write | Create expense offline → queued in IndexedDB → auto-sync when online |
| **PWA-4** | Background Sync | Service Worker syncs queue on `online` event; shows completion toast |
| **PWA-5** | Update Detection | New version detected → toast "Update available" → click to reload |
| **UX-1** | Thai Dates | All dates display in Buddhist Era (พ.ศ.) |
| **UX-2** | Thai Currency | All amounts display as "฿1,234" with comma separators |
| **UX-3** | Thai Language | All UI text in Thai |
| **UX-4** | Responsive | Works on 375px (iPhone SE) to 1920px+ without horizontal scroll |
| **PERF-1** | Lighthouse PWA | Score ≥ 90 |
| **PERF-2** | Lighthouse Performance | Score ≥ 80 |
| **AUTH-1** | Persist Session | Reload/close app → still logged in (token in localStorage + cookie) |
| **AUTH-2** | Auto Logout | 401 response → clear auth → redirect to login |
| **API-1** | Error Handling | Network error → toast + retry button; validation error → inline field messages |

---

## 11. Out of Scope (Future Enhancements)

- Push Notifications (requires VAPID keys, backend worker)
- Periodic Background Sync (menu price updates)
- Multi-user / Family sharing
- Expense splitting
- Bank/Receipt OCR integration
- Native iOS/Android app (this is PWA only)
- Advanced reporting / PDF export

---

## 12. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| iOS Safari PWA limitations (no background sync, limited storage) | High | Medium | Design offline queue to work with `online` event + manual sync button |
| PrimeVue Calendar Buddhist Era support | Medium | Low | Custom year/month navigator, or use native `<input type="date">` with conversion |
| IndexedDB quota exceeded | Low | High | Limit queue size, compress data, prompt user to sync |
| Flask session + JWT dual auth complexity | Medium | Medium | Start with session-only; add JWT for offline queue if needed |
| Vite build output to `../static` path issues on Windows | Low | Low | Use `path.resolve` in vite.config.ts, test on Windows |

---

## 13. Next Steps

1. **Review this spec** — Confirm approach, suggest changes
2. **Create implementation plan** — Invoke `writing-plans` skill for detailed task breakdown
3. **Scaffold frontend** — `npm create vite@latest frontend -- --template vue-ts`
4. **Configure PWA, PrimeVue, Pinia, Router, Axios**
5. **Implement stores, composables, API client**
6. **Build views & components** (priority: Dashboard → AddExpense → History → Analytics → Budget)
7. **Add Flask API endpoints & catch-all route**
8. **Test PWA features** (offline, install, sync)
9. **Lighthouse audit & polish**
10. **Deploy to staging/production**

---

**Document Location:** `docs/superpowers/specs/2026-08-21-thai-lunch-expense-pwa-design.md`  
**Git Commit:** Pending (awaiting approval)