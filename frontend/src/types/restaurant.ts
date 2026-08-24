export interface Restaurant {
  id: number;
  name: string;
  is_active: boolean;
  created_at?: string;
}

export interface Menu {
  id: number;
  restaurant_id: number;
  name: string;
  price: number;
  is_active: boolean;
}
