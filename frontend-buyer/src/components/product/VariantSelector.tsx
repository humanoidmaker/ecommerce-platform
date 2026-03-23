import type { ProductVariant, ProductAttribute } from "@/types/product";

interface Props {
  attributes: ProductAttribute[];
  variants: ProductVariant[];
  selectedVariant: ProductVariant | null;
  onSelect: (variant: ProductVariant) => void;
}

export function VariantSelector({ attributes, variants, selectedVariant, onSelect }: Props) {
  return (
    <div className="space-y-4">
      {attributes.map(attr => (
        <div key={attr.name}>
          <label className="text-sm font-medium text-gray-700">{attr.name}</label>
          <div className="flex flex-wrap gap-2 mt-1.5">
            {attr.values.map(val => {
              const isColor = attr.name.toLowerCase() === "color";
              const matching = variants.filter(v => v.attributes[attr.name] === val && v.is_active && v.available > 0);
              const isSelected = selectedVariant?.attributes[attr.name] === val;
              const isAvailable = matching.length > 0;

              return isColor ? (
                <button key={val} onClick={() => { const m = matching[0]; if (m) onSelect(m); }}
                  className={`w-8 h-8 rounded-full border-2 transition-all ${isSelected ? "border-blue-600 ring-2 ring-blue-200" : "border-gray-200"} ${!isAvailable ? "opacity-30" : ""}`}
                  style={{ backgroundColor: val.toLowerCase() }} title={val} disabled={!isAvailable} />
              ) : (
                <button key={val} onClick={() => { const m = matching[0]; if (m) onSelect(m); }}
                  className={`px-3 py-1.5 text-sm rounded-lg border transition-all ${isSelected ? "border-blue-600 bg-blue-50 text-blue-700 font-medium" : "border-gray-200 text-gray-600 hover:border-gray-400"} ${!isAvailable ? "opacity-30 line-through" : ""}`}
                  disabled={!isAvailable}>
                  {val}
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
