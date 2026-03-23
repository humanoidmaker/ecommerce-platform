import { Routes, Route } from "react-router-dom";
function P({ n }: { n: string }) { return <div className="flex items-center justify-center min-h-screen bg-gray-950 text-white"><h1 className="text-xl font-bold">{n}</h1></div>; }
export default function App() {
  return (<Routes>
    <Route path="/login" element={<P n="Admin Login" />} />
    <Route path="/" element={<P n="Dashboard" />} />
    <Route path="/users" element={<P n="Users" />} />
    <Route path="/sellers" element={<P n="Sellers" />} />
    <Route path="/products" element={<P n="Products" />} />
    <Route path="/categories" element={<P n="Categories" />} />
    <Route path="/orders" element={<P n="Orders" />} />
    <Route path="/warehouses" element={<P n="Warehouses" />} />
    <Route path="/coupons" element={<P n="Coupons" />} />
    <Route path="/reviews" element={<P n="Reviews" />} />
    <Route path="/commissions" element={<P n="Commissions" />} />
    <Route path="/analytics" element={<P n="Analytics" />} />
    <Route path="/system" element={<P n="System" />} />
    <Route path="/settings" element={<P n="Settings" />} />
  </Routes>);
}
