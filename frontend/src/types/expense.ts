export type ExpenseCategory = 'rice' | 'noodle' | 'snack' | 'drink' | 'fruit' | 'other';

export interface Expense {
  id: number;
  user_id: number;
  restaurant_id: number;
  menu_id: number;
  amount: number;
  category: ExpenseCategory;
  date: string;
  note?: string;
  created_at: string;
  
  // Expanded fields for frontend display
  restaurant?: {
    id: number;
    name: string;
  };
  menu?: {
    id: number;
    name: string;
  };
}

export interface ExpenseFormData {
  restaurant_id: number;
  menu_id: number;
  amount: number;
  category: ExpenseCategory;
  date: string;
  note?: string;
}

export interface ExpenseFilters {
  page?: number;
  per_page?: number;
  date_from?: string;
  date_to?: string;
  category?: ExpenseCategory;
  restaurant_id?: number;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  meta: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}
