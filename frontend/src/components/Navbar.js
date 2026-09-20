import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useShop } from '../context/ShopContext';
import './Navbar.css';

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { compareList, wishlist, cartCount } = useShop();
  const [search, setSearch] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);
  const submitSearch = (event) => { event.preventDefault(); navigate(`/products${search.trim() ? `?search=${encodeURIComponent(search.trim())}` : ''}`); setMenuOpen(false); };
  const active = (path) => path === '/' ? location.pathname === '/' : location.pathname.startsWith(path);
  return <header className="site-header"><div className="nav-shell"><Link to="/" className="brand-mark" onClick={() => setMenuOpen(false)}><span className="brand-symbol">j</span><span><strong>joyory</strong><small>SMART BEAUTY</small></span></Link><form className="nav-search" onSubmit={submitSearch}><i className="bi bi-search" /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search your next beauty find" aria-label="Search products" /></form><button className="menu-toggle" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle navigation"><i className={`bi ${menuOpen ? 'bi-x-lg' : 'bi-list'}`} /></button><nav className={`main-nav ${menuOpen ? 'is-open' : ''}`}><Link className={active('/') ? 'active' : ''} to="/" onClick={() => setMenuOpen(false)}>Home</Link><Link className={active('/products') ? 'active' : ''} to="/products" onClick={() => setMenuOpen(false)}>Shop</Link><Link to="/products?bestseller=true" onClick={() => setMenuOpen(false)}>Bestsellers</Link><Link to="/quiz" className="nav-match" onClick={() => setMenuOpen(false)}><i className="bi bi-stars" /> Find my match</Link><div className="nav-tools"><Link to="/wishlist" aria-label="Wishlist"><i className="bi bi-heart" />{wishlist.length > 0 && <b>{wishlist.length}</b>}</Link><Link to="/compare" aria-label="Compare"><i className="bi bi-intersect" />{compareList.length > 0 && <b>{compareList.length}</b>}</Link><Link to="/cart" aria-label="Shopping bag"><i className="bi bi-bag" />{cartCount > 0 && <b>{cartCount}</b>}</Link></div></nav></div></header>;
}
export default Navbar;
