import { Star } from "lucide-react";

interface Props { rating: number; count?: number; size?: "sm" | "md"; }

export function RatingStars({ rating, count, size = "sm" }: Props) {
  const s = size === "sm" ? "h-3.5 w-3.5" : "h-5 w-5";
  return (
    <div className="flex items-center gap-1">
      <div className="flex">
        {[1, 2, 3, 4, 5].map(i => (
          <Star key={i} className={`${s} ${i <= Math.round(rating) ? "fill-yellow-400 text-yellow-400" : "text-gray-200"}`} />
        ))}
      </div>
      {count !== undefined && <span className="text-xs text-gray-500">({count})</span>}
    </div>
  );
}
