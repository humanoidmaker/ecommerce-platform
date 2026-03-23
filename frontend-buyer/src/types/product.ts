export interface Product {
  id: string;
  title: string;
  slug: string;
  price: string;
  compare_at_price: string | null;
  average_rating: string;
  review_count: number;
  brand: string | null;
  condition: string;
  total_sold: number;
  image_url: string | null;
  thumbnail_url: string | null;
  is_featured: boolean;
  is_bestseller: boolean;
}

export interface ProductDetail extends Product {
  description: string | null;
  short_description: string | null;
  currency: string;
  tags: string[] | null;
  has_variants: boolean;
  weight_kg: string | null;
  view_count: number;
  is_digital: boolean;
}

export interface ProductVariant {
  id: string;
  name: string;
  sku: string;
  attributes: Record<string, string>;
  price: string | null;
  stock_quantity: number;
  reserved_quantity: number;
  available: number;
  is_active: boolean;
  image_id: string | null;
}

export interface ProductImage {
  id: string;
  url: string;
  thumbnail_url: string | null;
  alt_text: string;
  is_primary: boolean;
  sort_order: number;
}

export interface ProductAttribute {
  name: string;
  values: string[];
}

export interface ShippingOption {
  method: string;
  name: string;
  cost: string;
  min_days: number;
  max_days: number;
  free_shipping: boolean;
}

export interface ReviewSummary {
  1: number; 2: number; 3: number; 4: number; 5: number;
}

export interface Review {
  id: string;
  rating: number;
  title: string | null;
  body: string | null;
  helpful_count: number;
  is_verified: boolean;
  created_at: string;
}

export interface SellerInfo {
  id: string;
  store_name: string;
  store_slug: string;
  logo_url: string | null;
  average_rating: string;
  review_count: number;
  is_verified: boolean;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  icon_key: string | null;
  product_count: number;
  children?: Category[];
}
