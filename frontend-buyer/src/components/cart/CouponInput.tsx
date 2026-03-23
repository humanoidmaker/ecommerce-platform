import { useState } from "react";
import { Tag, X, Loader2 } from "lucide-react";

interface Props { onApply: (code: string) => Promise<void>; onRemove: () => void; appliedCode?: string; }

export function CouponInput({ onApply, onRemove, appliedCode }: Props) {
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleApply = async () => {
    if (!code.trim()) return;
    setError(""); setLoading(true);
    try { await onApply(code.trim()); setCode(""); }
    catch (e) { setError(e instanceof Error ? e.message : "Invalid coupon"); }
    finally { setLoading(false); }
  };

  if (appliedCode) {
    return (
      <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-lg px-3 py-2">
        <Tag className="h-3.5 w-3.5 text-green-600" />
        <span className="text-sm font-medium text-green-700 flex-1">{appliedCode}</span>
        <button onClick={onRemove} className="text-green-500 hover:text-red-500"><X className="h-3.5 w-3.5" /></button>
      </div>
    );
  }

  return (
    <div>
      <div className="flex gap-2">
        <input value={code} onChange={e => setCode(e.target.value.toUpperCase())} onKeyDown={e => e.key === "Enter" && handleApply()}
          placeholder="Coupon code" className="flex-1 h-9 px-3 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <button onClick={handleApply} disabled={loading} className="px-4 h-9 bg-gray-900 text-white text-sm rounded-lg hover:bg-gray-800 disabled:opacity-50">
          {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Apply"}
        </button>
      </div>
      {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
    </div>
  );
}
