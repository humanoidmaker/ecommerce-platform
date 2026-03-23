import { apiFetch } from "./client";
import type { Cart } from "@/types/cart";

export async function getCart() { return apiFetch<Cart>("/cart"); }
export async function addToCart(product_id: string, variant_id?: string, quantity = 1) { return apiFetch("/cart/items", { method: "POST", body: JSON.stringify({ product_id, variant_id, quantity }) }); }
export async function updateCartItem(item_id: string, quantity: number) { return apiFetch(`/cart/items/${item_id}`, { method: "PATCH", body: JSON.stringify({ quantity }) }); }
export async function removeCartItem(item_id: string) { return apiFetch(`/cart/items/${item_id}`, { method: "DELETE" }); }
export async function applyCoupon(code: string) { return apiFetch("/cart/coupon", { method: "POST", body: JSON.stringify({ code }) }); }
export async function removeCoupon() { return apiFetch("/cart/coupon", { method: "DELETE" }); }
