import { apiFetch } from "./client";
import type { Product, Category } from "@/types/product";

export async function getHomePage() { return apiFetch<{ featured: Product[]; bestsellers: Product[]; deals: Product[]; new_arrivals: Product[]; categories: Category[] }>("/catalog/home"); }
export async function getCategories() { return apiFetch<Category[]>("/catalog/categories"); }
export async function getCategoryTree() { return apiFetch<Category[]>("/catalog/categories/tree"); }
export async function getCategoryPage(slug: string, params: Record<string, string> = {}) {
  const q = new URLSearchParams(params);
  return apiFetch<{ category: Category; products: Product[]; total: number; subcategories: Category[]; breadcrumb: { id: string; name: string; slug: string }[] }>(`/catalog/categories/${slug}?${q}`);
}
