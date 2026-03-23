export interface Order {
  id: string;
  order_number: string;
  status: string;
  payment_status: string;
  grand_total: string;
  item_count: number;
  created_at: string;
}

export interface OrderDetail extends Order {
  subtotal: string;
  discount_total: string;
  tax_total: string;
  shipping_total: string;
  shipping_address: Record<string, string>;
  billing_address: Record<string, string>;
  coupon_code: string | null;
  cancellation_reason: string | null;
  items: OrderItemDetail[];
}

export interface OrderItemDetail {
  id: string;
  product_title: string;
  variant_name: string | null;
  image_url: string | null;
  sku: string | null;
  quantity: number;
  unit_price: string;
  total_price: string;
  status: string;
  tracking_number: string | null;
  shipped_at: string | null;
  delivered_at: string | null;
}

export interface TrackingEvent {
  status: string;
  location: string;
  timestamp: string;
  description: string;
}

export interface Shipment {
  id: string;
  tracking_number: string;
  carrier: string;
  status: string;
  estimated_delivery: string | null;
  events: TrackingEvent[];
}
