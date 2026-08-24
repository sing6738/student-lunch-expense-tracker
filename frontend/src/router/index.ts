import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue'), meta: { public: true } },
  { path: '/register', name: 'register', component: () => import('../views/RegisterView.vue'), meta: { public: true } },
  { path: '/', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
  { path: '/expenses/add', name: 'addExpense', component: () => import('../views/AddExpenseView.vue') },
  { path: '/expenses/add-multi', name: 'addMultiExpense', component: () => import('../views/AddMultiExpenseView.vue') },
  { path: '/expenses/:id/edit', name: 'editExpense', component: () => import('../views/EditExpenseView.vue') },
  { path: '/history', name: 'history', component: () => import('../views/HistoryView.vue') },
  { path: '/analytics', name: 'analytics', component: () => import('../views/AnalyticsView.vue') },
  { path: '/budget', name: 'budget', component: () => import('../views/BudgetView.vue') },
  { path: '/monthly-budget', name: 'monthlyBudget', component: () => import('../views/MonthlyBudgetView.vue') },
  { path: '/monthly-budget/summary', name: 'monthlyBudgetSummary', component: () => import('../views/MonthlyBudgetSummaryView.vue') },
  { path: '/orders', name: 'onlineOrders', component: () => import('../views/OnlineOrdersView.vue') },
  { path: '/manage-menus', name: 'manageMenus', component: () => import('../views/ManageMenusView.vue') },
  { path: '/profile', name: 'profile', component: () => import('../views/ProfileView.vue') },
  { path: '/:pathMatch(.*)*', name: 'notFound', component: () => import('../views/NotFoundView.vue'), meta: { public: true } }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Wait for auth to initialize if needed
  if (!authStore.isAuthenticated && authStore.token) {
    try {
        await authStore.fetchUser()
    } catch(e) {
        // failed to fetch user, token invalid
    }
  }

  const isPublic = to.meta.public
  const isAuthenticated = authStore.isAuthenticated

  if (!isPublic && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if ((to.name === 'login' || to.name === 'register') && isAuthenticated) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
