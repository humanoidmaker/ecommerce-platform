interface Props { price: string; compareAt: string | null; currency?: string; size?: "sm" | "md" | "lg"; }

export function PriceDisplay({ price, compareAt, size = "md" }: Props) {
  const hasDiscount = compareAt && parseFloat(compareAt) > parseFloat(price);
  const pct = hasDiscount ? Math.round((1 - parseFloat(price) / parseFloat(compareAt!)) * 100) : 0;
  const sizes = { sm: "text-sm", md: "text-lg", lg: "text-2xl" };

  return (
    <div className="flex items-center gap-2">
      <span className={`font-bold text-gray-900 ${sizes[size]}`}>${parseFloat(price).toFixed(2)}</span>
      {hasDiscount && (
        <>
          <span className="text-sm text-gray-400 line-through">${parseFloat(compareAt!).toFixed(2)}</span>
          <span className="text-xs font-semibold text-green-600 bg-green-50 px-1.5 py-0.5 rounded">-{pct}%</span>
        </>
      )}
    </div>
  );
}
