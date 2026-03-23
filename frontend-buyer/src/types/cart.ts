export interface CartItem {
  id: string;
  product_id: string;
  variant_id: string | null;
  product_title: string;
  variant_name: string | null;
  unit_price: string;
  quantity: number;
  total_price: string;
  image_url: string | null;
}

export interface Cart {
  id: string;
  item_count: number;
  subtotal: string;
  discount_total: string;
  tax_total: string;
  shipping_total: string;
  grand_total: string;
  items: CartItem[];
  warnings: CartWarning[];
}

export interface CartWarning {
  item_id: string;
  type: "removed" | "price_changed" | "out_of_stock" | "stock_reduced";
  message: string;
}
