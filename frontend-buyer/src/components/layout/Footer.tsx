export function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-400 py-12 mt-16">
      <div className="max-w-7xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8">
        <div>
          <h3 className="text-white font-bold mb-3">E-Commerce Platform</h3>
          <p className="text-sm">Your marketplace for everything.</p>
        </div>
        <div>
          <h4 className="text-white font-medium text-sm mb-2">Shop</h4>
          <ul className="space-y-1 text-sm"><li>Categories</li><li>Deals</li><li>New Arrivals</li><li>Bestsellers</li></ul>
        </div>
        <div>
          <h4 className="text-white font-medium text-sm mb-2">Account</h4>
          <ul className="space-y-1 text-sm"><li>Orders</li><li>Wishlist</li><li>Settings</li></ul>
        </div>
        <div>
          <h4 className="text-white font-medium text-sm mb-2">Sell</h4>
          <ul className="space-y-1 text-sm"><li>Become a Seller</li><li>Seller Dashboard</li></ul>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 mt-8 pt-6 border-t border-gray-800 text-center text-xs">E-Commerce Platform Marketplace</div>
    </footer>
  );
}
