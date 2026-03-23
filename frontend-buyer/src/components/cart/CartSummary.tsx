import { Link } from "react-router-dom";

interface Props { subtotal: string; discount: string; tax: string; shipping: string; total: string; }

export function CartSummary({ subtotal, discount, tax, shipping, total }: Props) {
  const row = (label: string, value: string, bold = false, red = false) => (
    <div className={`flex justify-between text-sm ${bold ? "font-bold text-gray-900 text-base pt-2 border-t border-gray-200" : "text-gray-600"}`}>
      <span>{label}</span>
      <span className={red ? "text-green-600" : ""}>{red ? "-" : ""}${parseFloat(value).toFixed(2)}</span>
    </div>
  );

  return (
    <div className="bg-gray-50 rounded-xl p-5 space-y-3">
      <h3 className="font-bold text-gray-900">Order Summary</h3>
      {row("Subtotal", subtotal)}
      {parseFloat(discount) > 0 && row("Discount", discount, false, true)}
      {row("Tax", tax)}
      {row("Shipping", parseFloat(shipping) > 0 ? shipping : "Free")}
      {row("Total", total, true)}
      <Link to="/checkout" className="block w-full h-11 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 flex items-center justify-center text-sm mt-4">
        Proceed to Checkout
      </Link>
    </div>
  );
}
