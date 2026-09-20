import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { useShop } from '../context/ShopContext';
import './Navbar.css';

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { compareList, wishlist, cartCount } = useShop();

  const urlSearch = location.pathname === '/products' ? (searchParams.get('search') || '') : '';
  const [search, setSearch] = useState(urlSearch);
  const [menuOpen, setMenuOpen] = useState(false);

  // Sync navbar search text if URL search param changes
  useEffect(() => {
    if (location.pathname === '/products') {
      setSearch(searchParams.get('search') || '');
    }
  }, [location.pathname, searchParams]);

  const submitSearch = (event) => {
    event.preventDefault();
    const query = search.trim();
    if (location.pathname === '/products') {
      // If already on products page, update search param preserving other filters or resetting
      navigate(`/products${query ? `?search=${encodeURIComponent(query)}` : ''}`);
    } else {
      navigate(`/products${query ? `?search=${encodeURIComponent(query)}` : ''}`);
    }
    setMenuOpen(false);
  };

  const clearSearch = () => {
    setSearch('');
    if (location.pathname === '/products') {
      navigate('/products');
    }
  };

  const active = (path) => path === '/' ? location.pathname === '/' : location.pathname.startsWith(path);

  return (
    <header className="site-header">
      <div className="nav-shell">
        <Link to="/" className="brand-mark" onClick={() => setMenuOpen(false)}>
          <span className="brand-symbol">j</span>
          <span>
            <strong>joyory</strong>
            <small>SMART BEAUTY</small>
          </span>
        </Link>

        {/* Global Navbar Search Bar */}
        <form className="nav-search" onSubmit={submitSearch}>
          <button type="submit" className="nav-search-btn" aria-label="Search">
            <i className="bi bi-search" />
          </button>
          <input
            id="nav-global-search"
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search products, ingredients, body care..."
            aria-label="Search products"
          />
          {search && (
            <button
              type="button"
              className="nav-search-clear"
              onClick={clearSearch}
              aria-label="Clear search"
            >
              <i className="bi bi-x" />
            </button>
          )}
        </form>

        <button
          className="menu-toggle"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle navigation"
        >
          <i className={`bi ${menuOpen ? 'bi-x-lg' : 'bi-list'}`} />
        </button>

        <nav className={`main-nav ${menuOpen ? 'is-open' : ''}`}>
          <Link className={active('/') ? 'active' : ''} to="/" onClick={() => setMenuOpen(false)}>
            Home
          </Link>
          <Link className={active('/products') ? 'active' : ''} to="/products" onClick={() => setMenuOpen(false)}>
            Shop
          </Link>
          <Link to="/products?bestseller=true" onClick={() => setMenuOpen(false)}>
            Bestsellers
          </Link>
          <Link to="/quiz" className="nav-match" onClick={() => setMenuOpen(false)}>
            <i className="bi bi-stars" /> Find my match
          </Link>

          <div className="nav-tools">
            <Link to="/wishlist" aria-label="Wishlist" title="Wishlist">
              <i className="bi bi-heart" />
              {wishlist.length > 0 && <b>{wishlist.length}</b>}
            </Link>
            <Link to="/compare" aria-label="Compare" title="Compare products">
              <i className="bi bi-intersect" />
              {compareList.length > 0 && <b>{compareList.length}</b>}
            </Link>
            <Link to="/cart" aria-label="Shopping bag" title="Cart">
              <i className="bi bi-bag" />
              {cartCount > 0 && <b>{cartCount}</b>}
            </Link>
          </div>
        </nav>
      </div>
    </header>
  );
}

export default Navbar;
