import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import { fetchCategories, fetchProducts } from '../services/api';
import { useShop } from '../context/ShopContext';
import './HomePage.css';

const categoryMeta = {
  skincare: { label: 'Skin rituals', note: 'Glow, hydrate, reset', icon: 'bi-droplet-half', tone: 'lavender' },
  haircare: { label: 'Hair rituals', note: 'Stronger, softer strands', icon: 'bi-wind', tone: 'peach' },
  makeup: { label: 'Makeup edit', note: 'Colour that feels like you', icon: 'bi-palette', tone: 'rose' },
  fragrance: { label: 'Scent wardrobe', note: 'Find your signature', icon: 'bi-flower1', tone: 'sage' },
  bodycare: { label: 'Body care', note: 'Small rituals, big comfort', icon: 'bi-stars', tone: 'sand' },
  nailcare: { label: 'Nail colour', note: 'The finishing touch', icon: 'bi-brush', tone: 'plum' },
};

function HomePage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const { cartCount } = useShop();

  useEffect(() => {
    Promise.all([fetchProducts(), fetchCategories()])
      .then(([productData, categoryData]) => {
        setProducts(Array.isArray(productData) ? productData : productData.results || []);
        setCategories(Array.isArray(categoryData) ? categoryData : categoryData.results || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const bestsellers = useMemo(() => products.filter((product) => product.is_bestseller).slice(0, 4), [products]);
  const newArrivals = useMemo(() => products.filter((product) => product.is_new_arrival).slice(0, 4), [products]);
  const featured = bestsellers.length ? bestsellers : products.slice(0, 4);

  return (
    <div className="home-page">
      <section className="home-hero">
        <div className="hero-video-bg" aria-hidden="true">
          <video autoPlay muted loop playsInline poster="https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=1000&q=85">
            <source src="/joyory-skincare-routine.mp4" type="video/mp4" />
          </video>
          <div className="hero-video-wash" />
        </div>
        <div className="hero-copy"><p className="eyebrow"><span className="eyebrow-dot" /> Beauty, but make it personal</p><h1>Good skin days<br /><em>start here.</em></h1><p className="hero-lede">Thoughtfully chosen beauty, matched to your real routine. Discover formulas that feel as good as they look.</p><div className="hero-actions"><Link to="/quiz" className="button button-dark">Find my match <i className="bi bi-arrow-up-right" /></Link><Link to="/products" className="text-link">Shop the edit <i className="bi bi-arrow-right" /></Link></div><div className="hero-proof"><div className="avatar-stack"><span>J</span><span>M</span><span>A</span><span>+</span></div><div><strong>Loved by 2,000+ beauty explorers</strong><small>Honest picks. No overwhelm.</small></div></div></div><div className="hero-visual"><div className="hero-orbit orbit-one" /><div className="hero-orbit orbit-two" /><div className="hero-image-frame"><img src="https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=1000&q=85" alt="Beauty products arranged on a warm peach background" /></div><div className="floating-note note-top"><span className="note-icon"><i className="bi bi-stars" /></span><span><strong>Curated for you</strong><small>Based on your needs</small></span></div><div className="floating-note note-bottom"><span className="rating-star">★</span><span><strong>4.8 / 5</strong><small>from our community</small></span></div><span className="hero-stamp">SMART<br /><b>MATCH</b></span></div>
      </section>
      <section className="trust-strip"><div><i className="bi bi-shield-check" /><span><strong>Ingredient-first</strong><small>Clear, considered formulas</small></span></div><div><i className="bi bi-magic" /><span><strong>Smart recommendations</strong><small>A routine that gets you</small></span></div><div><i className="bi bi-heart" /><span><strong>Beauty without pressure</strong><small>Explore at your own pace</small></span></div></section>
      <section className="home-section category-section"><div className="section-heading"><div><p className="eyebrow">Start with a feeling</p><h2>Shop your kind of beautiful</h2></div><Link to="/products" className="text-link">View all <i className="bi bi-arrow-right" /></Link></div><div className="category-grid">{(categories.length ? categories : Object.keys(categoryMeta)).slice(0, 6).map((item, index) => { const value = typeof item === 'string' ? item : item.value || item.slug || item.category; const meta = categoryMeta[value] || { label: value, note: 'Explore the collection', icon: 'bi-stars', tone: ['lavender', 'peach', 'rose', 'sage'][index % 4] }; return <Link to={`/products?category=${value}`} className={`category-tile ${meta.tone}`} key={value}><span className="category-icon"><i className={`bi ${meta.icon}`} /></span><span><strong>{meta.label}</strong><small>{meta.note}</small></span><i className="bi bi-arrow-up-right tile-arrow" /></Link>; })}</div></section>
      <section className="home-section featured-section"><div className="section-heading"><div><p className="eyebrow">The smart edit</p><h2>People are loving right now</h2></div><Link to="/products?bestseller=true" className="text-link">Shop bestsellers <i className="bi bi-arrow-right" /></Link></div>{loading ? <div className="loading-line">Curating your edit<span>...</span></div> : <div className="product-grid">{featured.map((product) => <ProductCard product={product} key={product.id} />)}</div>}</section>
      <section className="match-banner"><div className="match-copy"><p className="eyebrow">Not sure where to start?</p><h2>Your shelf,<br /><em>made smarter.</em></h2><p>Answer five quick questions and we’ll build a beauty edit around your skin, your pace, and your budget.</p><Link to="/quiz" className="button button-light">Take the 60-second quiz <i className="bi bi-arrow-up-right" /></Link></div><div className="match-visual"><div className="match-ring ring-one" /><div className="match-ring ring-two" /><div className="match-card"><span className="match-card-kicker">YOUR MATCH</span><strong>Soft glow<br />starter set</strong><span className="match-score"><i className="bi bi-stars" /> 96% match</span></div></div></section>
      {newArrivals.length > 0 && <section className="home-section new-section"><div className="section-heading"><div><p className="eyebrow">Fresh on the shelf</p><h2>New rituals to try</h2></div><Link to="/products?new=true" className="text-link">See everything new <i className="bi bi-arrow-right" /></Link></div><div className="product-grid">{newArrivals.map((product) => <ProductCard product={product} key={product.id} />)}</div></section>}
      <section className="home-footer-cta"><div><p className="eyebrow">A little beauty clarity</p><h2>Less scrolling.<br /><em>More finding.</em></h2><p>Compare, save, and build a routine you’ll actually come back to.</p></div><div className="cta-actions"><Link to="/products" className="button button-dark">Explore the shop <i className="bi bi-arrow-up-right" /></Link><Link to="/compare" className="text-link">Compare picks <i className="bi bi-arrow-right" /></Link></div><span className="bag-counter"><i className="bi bi-bag-heart" /> {cartCount || 0} in your bag</span></section>
    </div>
  );
}
export default HomePage;
