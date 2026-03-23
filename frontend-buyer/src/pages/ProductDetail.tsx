import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { ShoppingCart, Heart, Truck, Shield, Loader2, Minus, Plus } from "lucide-react";
import { apiFetch } from "@/api/client";
import { addToCart } from "@/api/cartApi";
import { ProductImageGallery } from "@/components/product/ProductImageGallery";
import { VariantSelector } from "@/components/product/VariantSelector";
import { PriceDisplay } from "@/components/product/PriceDisplay";
import { RatingStars } from "@/components/product/RatingStars";
import { ProductGrid } from "@/components/product/ProductGrid";
import type { ProductDetail as PD, ProductVariant, ProductImage, ProductAttribute, ShippingOption, SellerInfo, Product } from "@/types/product";

export default function ProductDetail() {
  const { slug } = useParams<{ slug: string }>();
  const [data, setData] = useState<{ product: PD; variants: ProductVariant[]; images: ProductImage[]; attributes: ProductAttribute[]; seller: SellerInfo | null; shipping_options: ShippingOption[]; related_products: Product[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [addingToCart, setAddingToCart] = useState(false);
  const [added, setAdded] = useState(false);

  useEffect(() => {
    if (!slug) return;
    apiFetch<typeof data>(`/products/${slug}`).then(d => { setData(d); if (d?.variants.length) setSelectedVariant(d.variants.find(v => v.available > 0) || null); }).catch(() => {}).finally(() => setLoading(false));
  }, [slug]);

  const handleAddToCart = async () => {
    if (!data) return;
    setAddingToCart(true);
    try {
      await addToCart(data.product.id, selectedVariant?.id, quantity);
      setAdded(true);
      setTimeout(() => setAdded(false), 2000);
    } catch { }
    finally { setAddingToCart(false); }
  };

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-blue-600" /></div>;
  if (!data) return <div className="text-center py-20">Product not found</div>;

  const { product, variants, images, attributes, seller, shipping_options, related_products } = data;
  const effectivePrice = selectedVariant?.price || product.price;
  const stock = selectedVariant ? selectedVariant.available : 999;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
        {/* Images */}
        <ProductImageGallery images={images} />

        {/* Info */}
        <div className="space-y-5">
          <h1 className="text-2xl font-bold text-gray-900">{product.title}</h1>
          <RatingStars rating={parseFloat(product.average_rating)} count={product.review_count} size="md" />
          <PriceDisplay price={effectivePrice} compareAt={product.compare_at_price} size="lg" />

          {/* Variants */}
          {attributes.length > 0 && (
            <VariantSelector attributes={attributes} variants={variants} selectedVariant={selectedVariant} onSelect={setSelectedVariant} />
          )}

          {/* Stock */}
          <div className={`text-sm font-medium ${stock > 5 ? "text-green-600" : stock > 0 ? "text-orange-500" : "text-red-600"}`}>
            {stock > 5 ? "In Stock" : stock > 0 ? `Only ${stock} left!` : "Out of Stock"}
          </div>

          {/* Quantity + Add to Cart */}
          <div className="flex items-center gap-3">
            <div className="flex items-center border border-gray-200 rounded-lg">
              <button onClick={() => setQuantity(q => Math.max(1, q - 1))} className="px-3 py-2"><Minus className="h-4 w-4" /></button>
              <span className="px-4 font-medium">{quantity}</span>
              <button onClick={() => setQuantity(q => Math.min(stock, q + 1))} className="px-3 py-2"><Plus className="h-4 w-4" /></button>
            </div>
            <button onClick={handleAddToCart} disabled={stock === 0 || addingToCart}
              className={`flex-1 h-12 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all ${added ? "bg-green-500 text-white" : stock === 0 ? "bg-gray-200 text-gray-500 cursor-not-allowed" : "bg-blue-600 text-white hover:bg-blue-700"}`}>
              {addingToCart ? <Loader2 className="h-4 w-4 animate-spin" /> : added ? "✓ Added!" : <><ShoppingCart className="h-4 w-4" /> Add to Cart</>}
            </button>
            <button className="h-12 w-12 border border-gray-200 rounded-xl flex items-center justify-center text-gray-400 hover:text-red-500 hover:border-red-200">
              <Heart className="h-5 w-5" />
            </button>
          </div>

          {/* Shipping estimate */}
          <div className="border border-gray-200 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2 text-sm font-medium text-gray-900"><Truck className="h-4 w-4" /> Delivery Options</div>
            {shipping_options.map(s => (
              <div key={s.method} className="flex justify-between text-sm text-gray-600">
                <span>{s.name} ({s.min_days}-{s.max_days} days)</span>
                <span className="font-medium">{s.free_shipping ? "FREE" : `$${parseFloat(s.cost).toFixed(2)}`}</span>
              </div>
            ))}
          </div>

          {/* Seller info */}
          {seller && (
            <div className="border border-gray-200 rounded-xl p-4 flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center text-sm font-bold">{seller.store_name[0]}</div>
              <div className="flex-1">
                <p className="text-sm font-medium">{seller.store_name} {seller.is_verified && "✓"}</p>
                <RatingStars rating={parseFloat(seller.average_rating)} count={seller.review_count} />
              </div>
            </div>
          )}

          {/* Description */}
          {product.description && (
            <div className="prose prose-sm max-w-none text-gray-600" dangerouslySetInnerHTML={{ __html: product.description }} />
          )}
        </div>
      </div>

      {/* Related */}
      {related_products.length > 0 && (
        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Related Products</h2>
          <ProductGrid products={related_products} />
        </section>
      )}
    </div>
  );
}
