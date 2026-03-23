import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Search, ShoppingCart, Heart, User, Menu } from "lucide-react";

interface Props { cartCount: number; user: { first_name: string } | null; onLogout: () => void; }

export function Header({ cartCount, user, onLogout }: Props) {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();
  const handleSearch = (e: React.FormEvent) => { e.preventDefault(); if (query.trim()) navigate(`/search?q=${encodeURIComponent(query)}`); };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center gap-4">
        <Link to="/" className="text-xl font-black text-blue-600 shrink-0">E-Commerce Platform</Link>

        <form onSubmit={handleSearch} className="flex-1 max-w-2xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search products..."
              className="w-full h-10 pl-10 pr-4 rounded-full border border-gray-200 bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white" />
          </div>
        </form>

        <div className="flex items-center gap-3">
          <Link to="/wishlist" className="p-2 text-gray-500 hover:text-gray-900"><Heart className="h-5 w-5" /></Link>
          <Link to="/cart" className="relative p-2 text-gray-500 hover:text-gray-900">
            <ShoppingCart className="h-5 w-5" />
            {cartCount > 0 && <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-blue-600 text-white text-[10px] flex items-center justify-center font-bold">{cartCount}</span>}
          </Link>
          {user ? (
            <div className="flex items-center gap-2">
              <Link to="/orders" className="text-sm text-gray-600 hover:text-gray-900">Orders</Link>
              <button onClick={onLogout} className="text-sm text-gray-500 hover:text-red-600">Logout</button>
            </div>
          ) : (
            <Link to="/login" className="flex items-center gap-1 text-sm font-medium text-gray-700 hover:text-blue-600"><User className="h-4 w-4" /> Sign in</Link>
          )}
        </div>
      </div>
    </header>
  );
}
