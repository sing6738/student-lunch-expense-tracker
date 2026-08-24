export interface User {
  id: number;
  username: string;
  email?: string;
  daily_budget: number;
  wishlist_name?: string;
  wishlist_price?: number;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

export interface LoginResponse {
  success: boolean;
  data: {
    user: User;
    token: string;
  };
}
