import { Minus, Plus, Trash2 } from "lucide-react";
import type { CartItem } from "@/types/cart";

interface Props { item: CartItem; onUpdateQty: (id: string, qty: number) => void; onRemove: (id: string) => void; }

export function CartItemRow({ item, onUpdateQty, onRemove }: Props) {
  return (
    <div className="flex gap-4 py-4 border-b border-gray-100">
      <div className="w-20 h-20 bg-gray-50 rounded-lg overflow-hidden shrink-0">
        {item.image_url ? <img src={item.image_url} alt="" className="w-full h-full object-contain p-2" /> : <div className="w-full h-full flex items-center justify-center text-2xl">📦</div>}
      </div>
      <div className="flex-1 min-w-0">
        <h3 className="text-sm font-medium text-gray-900 truncate">{item.product_title}</h3>
        {item.variant_name && <p className="text-xs text-gray-500">{item.variant_name}</p>}
        <p className="text-sm font-semibold text-gray-900 mt-1">${parseFloat(item.unit_price).toFixed(2)}</p>
      </div>
      <div className="flex items-center gap-2">
        <div className="flex items-center border border-gray-200 rounded-lg">
          <button onClick={() => onUpdateQty(item.id, Math.max(1, item.quantity - 1))} className="px-2 py-1 text-gray-500 hover:text-gray-900"><Minus className="h-3 w-3" /></button>
          <span className="px-2 text-sm font-medium w-8 text-center">{item.quantity}</span>
          <button onClick={() => onUpdateQty(item.id, item.quantity + 1)} className="px-2 py-1 text-gray-500 hover:text-gray-900"><Plus className="h-3 w-3" /></button>
        </div>
        <span className="text-sm font-bold w-20 text-right">${parseFloat(item.total_price).toFixed(2)}</span>
        <button onClick={() => onRemove(item.id)} className="p-1 text-gray-400 hover:text-red-500"><Trash2 className="h-4 w-4" /></button>
      </div>
    </div>
  );
}
