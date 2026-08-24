export interface OnlineOrder {
  id: number;
  platform: string;
  store_name: string;
  item_name: string;
  price: number;
  shipping_cost: number;
  status: string;
  order_date: string;
  tracking_number?: string;
  note?: string;
}

export interface OnlineOrderFormData {
  platform: string;
  store_name: string;
  item_name: string;
  price: number;
  shipping_cost?: number;
  status?: string;
  date?: string;
  tracking_number?: string;
  note?: string;
}
