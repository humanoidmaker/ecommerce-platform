import { Routes, Route } from "react-router-dom";
import { Header } from "./components/layout/Header";
import { Footer } from "./components/layout/Footer";
import Home from "./pages/Home";
import Login from "./pages/Login";
import ProductDetail from "./pages/ProductDetail";
import Search from "./pages/Search";
import Cart from "./pages/Cart";
import Checkout from "./pages/Checkout";

function P({ n }: { n: string }) { return <div className="flex items-center justify-center min-h-[60vh]"><h1 className="text-xl font-bold text-gray-400">{n} — Phase 6</h1></div>; }

export default function App() {
  // Simplified — in production, use AuthContext
  const user = null;
  return (
    <div className="min-h-screen flex flex-col">
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<P n="Register" />} />
        <Route path="*" element={
          <>
            <Header cartCount={0} user={user} onLogout={() => {}} />
            <main className="flex-1">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/product/:slug" element={<ProductDetail />} />
                <Route path="/search" element={<Search />} />
                <Route path="/cart" element={<Cart />} />
                <Route path="/checkout" element={<Checkout />} />
                <Route path="/category/:slug" element={<P n="Category" />} />
                <Route path="/orders" element={<P n="Orders" />} />
                <Route path="/orders/:id" element={<P n="Order Detail" />} />
                <Route path="/wishlist" element={<P n="Wishlist" />} />
                <Route path="/seller/:slug" element={<P n="Seller Store" />} />
              </Routes>
            </main>
            <Footer />
          </>
        } />
      </Routes>
    </div>
  );
}
