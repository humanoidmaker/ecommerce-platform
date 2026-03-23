import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ChevronRight, Loader2 } from "lucide-react";
import { getHomePage } from "@/api/catalogApi";
import { ProductCard } from "@/components/product/ProductCard";
import type { Product, Category } from "@/types/product";

export default function Home() {
  const [data, setData] = useState<{ featured: Product[]; bestsellers: Product[]; deals: Product[]; new_arrivals: Product[]; categories: Category[] } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { getHomePage().then(setData).catch(() => {}).finally(() => setLoading(false)); }, []);

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-blue-600" /></div>;

  const Section = ({ title, products, link }: { title: string; products: Product[]; link?: string }) => (
    <section className="mb-12">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">{title}</h2>
        {link && <Link to={link} className="text-sm text-blue-600 hover:underline flex items-center">See all <ChevronRight className="h-4 w-4" /></Link>}
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {products.map(p => <ProductCard key={p.id} product={p} />)}
      </div>
    </section>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Hero */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 md:p-12 mb-12 text-white">
        <h1 className="text-3xl md:text-5xl font-black mb-3">Shop the Marketplace</h1>
        <p className="text-blue-100 text-lg mb-6">Thousands of products from verified sellers</p>
        <Link to="/search?q=" className="inline-block bg-white text-blue-600 font-semibold px-6 py-3 rounded-xl hover:bg-blue-50">Browse All Products</Link>
      </div>

      {/* Categories */}
      {data?.categories && data.categories.length > 0 && (
        <section className="mb-12">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Shop by Category</h2>
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
            {data.categories.map(c => (
              <Link key={c.id} to={`/category/${c.slug}`} className="bg-gray-50 rounded-xl p-4 text-center hover:bg-blue-50 hover:shadow-sm transition-all">
                <div className="text-2xl mb-1">🏷️</div>
                <p className="text-xs font-medium text-gray-700">{c.name}</p>
                <p className="text-[10px] text-gray-400">{c.product_count} items</p>
              </Link>
            ))}
          </div>
        </section>
      )}

      {data?.deals && data.deals.length > 0 && <Section title="🔥 Deals" products={data.deals} />}
      {data?.featured && data.featured.length > 0 && <Section title="Featured Products" products={data.featured} />}
      {data?.bestsellers && data.bestsellers.length > 0 && <Section title="Bestsellers" products={data.bestsellers} />}
      {data?.new_arrivals && data.new_arrivals.length > 0 && <Section title="New Arrivals" products={data.new_arrivals} />}
    </div>
  );
}
