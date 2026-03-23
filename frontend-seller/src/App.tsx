import { Routes, Route } from "react-router-dom";
function P({ n }: { n: string }) { return <div className="flex items-center justify-center min-h-screen bg-gray-50"><h1 className="text-xl font-bold">{n}</h1></div>; }
export default function App() {
  return (<Routes>
    <Route path="/login" element={<P n="Seller Login" />} />
    <Route path="/" element={<P n="Seller Dashboard" />} />
    <Route path="/store" element={<P n="Store Settings" />} />
    <Route path="/products" element={<P n="Products" />} />
    <Route path="/products/new" element={<P n="New Product" />} />
    <Route path="/products/:id" element={<P n="Edit Product" />} />
    <Route path="/inventory" element={<P n="Inventory" />} />
    <Route path="/orders" element={<P n="Orders" />} />
    <Route path="/orders/:id" element={<P n="Order Detail" />} />
    <Route path="/analytics" element={<P n="Analytics" />} />
    <Route path="/payouts" element={<P n="Payouts" />} />
    <Route path="/reviews" element={<P n="Reviews" />} />
    <Route path="/coupons" element={<P n="Coupons" />} />
  </Routes>);
}
