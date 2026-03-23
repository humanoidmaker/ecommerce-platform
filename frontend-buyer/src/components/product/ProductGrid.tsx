import { ProductCard } from "./ProductCard";
import type { Product } from "@/types/product";

interface Props { products: Product[]; }

export function ProductGrid({ products }: Props) {
  if (!products.length) return <div className="text-center py-20 text-gray-400">No products found</div>;
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      {products.map(p => <ProductCard key={p.id} product={p} />)}
    </div>
  );
}
