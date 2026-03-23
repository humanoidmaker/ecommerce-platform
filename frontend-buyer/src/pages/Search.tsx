import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { apiFetch } from "@/api/client";
import { ProductGrid } from "@/components/product/ProductGrid";
import type { Product } from "@/types/product";

export default function Search() {
  const [params] = useSearchParams();
  const query = params.get("q") || "";
  const [products, setProducts] = useState<Product[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [sort, setSort] = useState("relevance");

  useEffect(() => {
    if (!query) return;
    setLoading(true);
    apiFetch<{ results: Product[]; total: number }>(`/search?q=${encodeURIComponent(query)}&sort=${sort}`)
      .then(d => { setProducts(d.results); setTotal(d.total); })
      .catch(() => {}).finally(() => setLoading(false));
  }, [query, sort]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold">Results for "{query}"</h1>
          <p className="text-sm text-gray-500">{total} products found</p>
        </div>
        <select value={sort} onChange={e => setSort(e.target.value)} className="h-9 px-3 border border-gray-200 rounded-lg text-sm">
          <option value="relevance">Relevance</option>
          <option value="price_low">Price: Low to High</option>
          <option value="price_high">Price: High to Low</option>
          <option value="rating">Highest Rated</option>
          <option value="newest">Newest</option>
          <option value="bestselling">Bestselling</option>
        </select>
      </div>
      {loading ? <div className="flex justify-center py-20"><Loader2 className="h-6 w-6 animate-spin text-blue-600" /></div> : <ProductGrid products={products} />}
    </div>
  );
}
