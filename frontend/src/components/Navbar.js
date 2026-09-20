import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useShop } from '../context/ShopContext';
import './Navbar.css';

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { wishlist, cartCount, compareList } = useShop();
  const [navSearch, setNavSearch] = useState('');
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const isActive = (path) => location.pathname === path;

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (navSearch.trim()) {
      navigate(`/products?search=${encodeURIComponent(navSearch.trim())}`);
      setNavSearch('');
    }
  };

  return (
    <header className={`sm-navbar-wrapper fixed-top ${scrolled ? 'is-scrolled' : ''}`}>
      <div className="container">
        <nav className="navbar navbar-expand-lg navbar-dark p-0">
          <Link className="navbar-brand sm-brand" to="/">
            <div className="brand-logo-glow">
              <i className="bi bi-stars"></i>
            </div>
            <div className="brand-titles">
              <span className="brand-name">
                <span className="brand-gradient">Joyory</span>
                <span className="brand-match">SmartMatch</span>
              </span>
              <span className="brand-tagline">BEAUTY INTELLIGENCE</span>
            </div>
          </Link>

          {/* Quick Search Bar in Navbar */}
          <form className="nav-search-bar d-none d-xl-flex" onSubmit={handleSearchSubmit}>
            <i className="bi bi-search search-icon"></i>
            <input
              type="text"
              placeholder="Search serums, niacinamide, lipstick..."
              value={navSearch}
              onChange={(e) => setNavSearch(e.target.value)}
              className="nav-search-input"
            />
            {navSearch && (
              <button
                type="button"
                className="nav-search-clear"
                onClick={() => setNavSearch('')}
              >
                <i className="bi bi-x"></i>
              </button>
            )}
          </form>

          <button
            className="navbar-toggler border-0 p-2"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarNav"
            aria-controls="navbarNav"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-custom">
              <i className="bi bi-list"></i>
            </span>
          </button>

          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ms-auto align-items-lg-center gap-1">
              <li className="nav-item">
                <Link
                  className={`nav-link sm-nav-link ${isActive('/') ? 'active' : ''}`}
                  to="/"
                >
                  <i className="bi bi-house me-1"></i> Home
                </Link>
              </li>
              <li className="nav-item">
                <Link
                  className={`nav-link sm-nav-link ${isActive('/products') && !location.search ? 'active' : ''}`}
                  to="/products"
                >
                  <i className="bi bi-grid me-1"></i> Shop
                </Link>
              </li>
              <li className="nav-item">
                <Link
                  className={`nav-link sm-nav-link ${location.search.includes('bestseller=true') ? 'active' : ''}`}
                  to="/products?bestseller=true"
                >
                  <i className="bi bi-fire text-danger me-1"></i> Bestsellers
                </Link>
              </li>

              {/* Utility Badges: Compare, Wishlist, Bag */}
              <li className="nav-item">
                <Link
                  className={`nav-link sm-nav-icon-link ${isActive('/compare') ? 'active' : ''}`}
                  to="/compare"
                  title="Product Comparison"
                >
                  <i className="bi bi-intersect"></i>
                  {compareList.length > 0 && (
                    <span className="nav-count-badge badge-violet">{compareList.length}</span>
                  )}
                </Link>
              </li>

              <li className="nav-item">
                <Link
                  className={`nav-link sm-nav-icon-link ${isActive('/wishlist') ? 'active' : ''}`}
                  to="/wishlist"
                  title="My Wishlist"
                >
                  <i className="bi bi-heart"></i>
                  {wishlist.length > 0 && (
                    <span className="nav-count-badge badge-rose">{wishlist.length}</span>
                  )}
                </Link>
              </li>

              <li className="nav-item">
                <Link
                  className={`nav-link sm-nav-icon-link ${isActive('/cart') ? 'active' : ''}`}
                  to="/cart"
                  title="Beauty Bag"
                >
                  <i className="bi bi-bag"></i>
                  {cartCount > 0 && (
                    <span className="nav-count-badge badge-emerald">{cartCount}</span>
                  )}
                </Link>
              </li>

              <li className="nav-item ms-lg-2 mt-2 mt-lg-0">
                <Link to="/quiz" className="btn-glow nav-cta-btn">
                  <i className="bi bi-magic me-1"></i>
                  <span>Find My Match</span>
                </Link>
              </li>
            </ul>
          </div>
        </nav>
      </div>
    </header>
  );
}

export default Navbar;
