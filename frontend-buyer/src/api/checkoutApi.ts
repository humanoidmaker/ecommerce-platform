import { apiFetch } from "./client";
import type { ShippingOption } from "@/types/product";

export async function getShippingOptions() { return apiFetch<ShippingOption[]>("/checkout/shipping-options"); }
export async function placeOrder(data: { shipping_address: Record<string, string>; billing_address: Record<string, string>; shipping_method: string; payment_method: string }) {
  return apiFetch<{ order_id: string; order_number: string; payment_id: string; grand_total: string }>("/checkout/place-order", { method: "POST", body: JSON.stringify(data) });
}
export async function confirmPayment(order_id: string, payment_id: string) {
  return apiFetch<{ success: boolean; order_status: string; order_number: string }>("/checkout/confirm-payment", { method: "POST", body: JSON.stringify({ order_id, payment_id }) });
}
