import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { useShop } from '../context/ShopContext';
import { fetchProducts } from '../services/api';
import './Navbar.css';

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { compareList, wishlist, cartCount } = useShop();

  const urlSearch = location.pathname === '/products' ? (searchParams.get('search') || '') : '';
  const [search, setSearch] = useState(urlSearch);
  const [suggestions, setSuggestions] = useState([]);
  const [searchFocused, setSearchFocused] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  // Sync navbar search text if URL search param changes
  useEffect(() => {
    if (location.pathname === '/products') {
      setSearch(searchParams.get('search') || '');
    }
  }, [location.pathname, searchParams]);

  useEffect(() => {
    const query = search.trim();
    if (query.length < 2) {
      setSuggestions([]);
      return undefined;
    }
    let cancelled = false;
    const timer = setTimeout(async () => {
      try {
        const data = await fetchProducts({ search: query });
        if (!cancelled) setSuggestions((data.results || []).slice(0, 5));
      } catch (error) {
        if (!cancelled) setSuggestions([]);
      }
    }, 260);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [search]);

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
    setSearchFocused(false);
    setSuggestions([]);
  };

  const clearSearch = () => {
    setSearch('');
    if (location.pathname === '/products') {
      navigate('/products');
    }
    setSuggestions([]);
  };

  const openSuggestion = (product) => {
    navigate(`/products/${product.id}`);
    setSearchFocused(false);
    setSuggestions([]);
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
        <form className={`nav-search ${searchFocused ? 'is-focused' : ''}`} onSubmit={submitSearch}>
          <button type="submit" className="nav-search-btn" aria-label="Search">
            <i className="bi bi-search" />
          </button>
          <input
            id="nav-global-search"
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setTimeout(() => setSearchFocused(false), 180)}
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
          {searchFocused && search.trim().length >= 2 && (
            <div className="nav-search-results">
              {suggestions.length > 0 ? suggestions.map((product) => (
                <button type="button" className="nav-search-result" key={product.id} onMouseDown={() => openSuggestion(product)}>
                  <img src={product.image_url} alt="" />
                  <span><strong>{product.name}</strong><small>{product.brand} · ₹{product.discounted_price || product.price}</small></span>
                  <i className="bi bi-arrow-up-right" />
                </button>
              )) : <div className="nav-search-empty"><i className="bi bi-search me-2" />No matching products yet</div>}
              <button type="submit" className="nav-search-see-all">See all results for “{search.trim()}” <i className="bi bi-arrow-right" /></button>
            </div>
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
          <Link to="/dashboard" className={`${active('/dashboard') ? 'active' : ''}`} onClick={() => setMenuOpen(false)}>
            Dashboard
          </Link>

          {/* Beauty Tools Dropdown */}
          <div className="nav-tools-dropdown">
            <button className="nav-tools-trigger" aria-label="Beauty tools menu">
              <i className="bi bi-grid-3x3-gap" /> Tools <i className="bi bi-chevron-down tools-chevron" />
            </button>
            <div className="nav-tools-menu">
              <Link to="/routine" className="nav-tools-item" onClick={() => setMenuOpen(false)}>
                <i className="bi bi-calendar3 nav-tool-icon" />
                <div>
                  <strong>Routine Builder</strong>
                  <small>Build your AM &amp; PM routine</small>
                </div>
              </Link>
              <Link to="/ingredient-check" className="nav-tools-item" onClick={() => setMenuOpen(false)}>
                <i className="bi bi-shield-check nav-tool-icon" />
                <div>
                  <strong>Ingredient Checker</strong>
                  <small>Check ingredient conflicts</small>
                </div>
              </Link>
              <Link to="/compare" className="nav-tools-item" onClick={() => setMenuOpen(false)}>
                <i className="bi bi-intersect nav-tool-icon" />
                <div>
                  <strong>Compare Products</strong>
                  <small>Side-by-side evaluation</small>
                </div>
              </Link>
              <Link to="/reviews" className="nav-tools-item" onClick={() => setMenuOpen(false)}>
                <i className="bi bi-bar-chart nav-tool-icon" />
                <div>
                  <strong>Review Insights</strong>
                  <small>Rating &amp; catalog analysis</small>
                </div>
              </Link>
            </div>
          </div>

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
