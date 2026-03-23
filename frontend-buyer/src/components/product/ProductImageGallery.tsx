import { useState } from "react";
import type { ProductImage } from "@/types/product";

interface Props { images: ProductImage[]; }

export function ProductImageGallery({ images }: Props) {
  const [active, setActive] = useState(0);
  if (!images.length) return <div className="aspect-square bg-gray-100 rounded-xl flex items-center justify-center text-6xl text-gray-200">📦</div>;

  return (
    <div className="space-y-3">
      {/* Main image */}
      <div className="aspect-square bg-gray-50 rounded-xl overflow-hidden border border-gray-100">
        <img src={images[active]?.url} alt={images[active]?.alt_text || ""} className="w-full h-full object-contain p-4" />
      </div>
      {/* Thumbnails */}
      {images.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {images.map((img, i) => (
            <button key={img.id} onClick={() => setActive(i)}
              className={`w-16 h-16 rounded-lg border-2 overflow-hidden shrink-0 ${i === active ? "border-blue-500" : "border-gray-200 hover:border-gray-400"}`}>
              <img src={img.thumbnail_url || img.url} alt="" className="w-full h-full object-contain p-1" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
