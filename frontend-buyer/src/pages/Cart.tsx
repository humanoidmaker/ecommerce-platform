import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ShoppingCart, Loader2, AlertTriangle } from "lucide-react";
import { getCart, updateCartItem, removeCartItem, applyCoupon, removeCoupon } from "@/api/cartApi";
import { CartItemRow } from "@/components/cart/CartItemRow";
import { CartSummary } from "@/components/cart/CartSummary";
import { CouponInput } from "@/components/cart/CouponInput";
import type { Cart as CartType } from "@/types/cart";

export default function Cart() {
  const [cart, setCart] = useState<CartType | null>(null);
  const [loading, setLoading] = useState(true);

  const load = () => { setLoading(true); getCart().then(setCart).catch(() => {}).finally(() => setLoading(false)); };
  useEffect(load, []);

  const handleUpdateQty = async (id: string, qty: number) => { await updateCartItem(id, qty); load(); };
  const handleRemove = async (id: string) => { await removeCartItem(id); load(); };
  const handleApplyCoupon = async (code: string) => { await applyCoupon(code); load(); };
  const handleRemoveCoupon = async () => { await removeCoupon(); load(); };

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-blue-600" /></div>;

  if (!cart || cart.items.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <ShoppingCart className="h-16 w-16 text-gray-200 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-gray-900 mb-2">Your cart is empty</h2>
        <p className="text-gray-500 mb-6">Browse our products and find something you love!</p>
        <Link to="/" className="inline-block bg-blue-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-blue-700">Continue Shopping</Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Shopping Cart ({cart.item_count} items)</h1>

      {/* Warnings */}
      {cart.warnings.length > 0 && (
        <div className="mb-4 space-y-2">
          {cart.warnings.map((w, i) => (
            <div key={i} className="flex items-center gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-700">
              <AlertTriangle className="h-4 w-4 shrink-0" /> {w.message}
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          {cart.items.map(item => (
            <CartItemRow key={item.id} item={item} onUpdateQty={handleUpdateQty} onRemove={handleRemove} />
          ))}
        </div>

        <div className="space-y-4">
          <CouponInput onApply={handleApplyCoupon} onRemove={handleRemoveCoupon} />
          <CartSummary subtotal={cart.subtotal} discount={cart.discount_total} tax={cart.tax_total} shipping={cart.shipping_total} total={cart.grand_total} />
        </div>
      </div>
    </div>
  );
}
