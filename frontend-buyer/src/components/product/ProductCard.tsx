import { Link } from "react-router-dom";
import { Heart, ShoppingCart } from "lucide-react";
import { PriceDisplay } from "./PriceDisplay";
import { RatingStars } from "./RatingStars";
import type { Product } from "@/types/product";

interface Props { product: Product; onAddToCart?: () => void; }

export function ProductCard({ product, onAddToCart }: Props) {
  return (
    <div className="group bg-white rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg hover:border-gray-200 transition-all">
      <Link to={`/product/${product.slug}`} className="block relative aspect-square bg-gray-50">
        {product.image_url ? (
          <img src={product.image_url} alt={product.title} className="w-full h-full object-contain p-4 group-hover:scale-105 transition-transform" loading="lazy" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-300 text-4xl">📦</div>
        )}
        {/* Badges */}
        <div className="absolute top-2 left-2 flex flex-col gap-1">
          {product.is_bestseller && <span className="bg-orange-500 text-white text-[10px] font-bold px-2 py-0.5 rounded">BESTSELLER</span>}
          {product.compare_at_price && parseFloat(product.compare_at_price) > parseFloat(product.price) && (
            <span className="bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded">
              -{Math.round((1 - parseFloat(product.price) / parseFloat(product.compare_at_price)) * 100)}%
            </span>
          )}
        </div>
        {/* Wishlist */}
        <button className="absolute top-2 right-2 p-1.5 bg-white/80 rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white">
          <Heart className="h-4 w-4 text-gray-400 hover:text-red-500" />
        </button>
      </Link>

      <div className="p-3 space-y-1.5">
        <Link to={`/product/${product.slug}`} className="block">
          <h3 className="text-sm font-medium text-gray-900 line-clamp-2 group-hover:text-blue-600">{product.title}</h3>
        </Link>
        <RatingStars rating={parseFloat(product.average_rating)} count={product.review_count} />
        <PriceDisplay price={product.price} compareAt={product.compare_at_price} size="sm" />
        {onAddToCart && (
          <button onClick={onAddToCart} className="w-full mt-2 h-8 bg-blue-600 text-white text-xs font-medium rounded-lg hover:bg-blue-700 flex items-center justify-center gap-1 transition-colors">
            <ShoppingCart className="h-3 w-3" /> Add to Cart
          </button>
        )}
      </div>
    </div>
  );
}
