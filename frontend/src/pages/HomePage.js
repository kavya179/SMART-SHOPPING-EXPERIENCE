import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { fetchProducts } from '../services/api';
import ProductCard from '../components/ProductCard';
import { LoadingState, ErrorState } from '../components/StateDisplay';
import './HomePage.css';

const CATEGORIES = [
  { id: 'skincare', name: 'Skincare', icon: 'bi-droplet-half', color: '#7c5cfc', desc: 'Serums, Creams & Gels' },
  { id: 'haircare', name: 'Haircare', icon: 'bi-scissors', color: '#38bdf8', desc: 'Keratin, Biotin & Oils' },
  { id: 'makeup', name: 'Makeup', icon: 'bi-brush', color: '#ff4d6d', desc: 'Lipsticks & Foundations' },
  { id: 'fragrance', name: 'Fragrance', icon: 'bi-flower1', color: '#a855f7', desc: 'Parfums & Mists' },
  { id: 'bodycare', name: 'Body Care', icon: 'bi-heart-pulse', color: '#fb923c', desc: 'Scrubs & Lotions' },
  { id: 'nailcare', name: 'Nail Care', icon: 'bi-palette', color: '#ec4899', desc: 'Gel Polishes & Oils' },
];

function HomePage() {
  const navigate = useNavigate();
  const [bestsellers, setBestsellers] = useState([]);
  const [newArrivals, setNewArrivals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [heroSearch, setHeroSearch] = useState('');

  const loadFeatured = async () => {
    setLoading(true);
    setError(null);
    try {
      const [bestData, newData] = await Promise.all([
        fetchProducts({ bestseller: 'true', ordering: '-rating' }),
        fetchProducts({ new: 'true', ordering: '-rating' }),
      ]);
      setBestsellers(bestData.results || []);
      setNewArrivals(newData.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFeatured();
  }, []);

  const handleHeroSearch = (e) => {
    e.preventDefault();
    if (heroSearch.trim()) {
      navigate(`/products?search=${encodeURIComponent(heroSearch.trim())}`);
    } else {
      navigate('/products');
    }
  };

  return (
    <div className="home-page-container">
      {/* ── Editorial Hero ────────────────────────────────────── */}
      <section className="luxury-hero">
        <div className="hero-mesh-orb orb-purple"></div>
        <div className="hero-mesh-orb orb-pink"></div>
        <div className="hero-mesh-orb orb-emerald"></div>

        <div className="container position-relative z-2">
          <div className="row align-items-center gy-5">
            <div className="col-lg-7">
              <div className="animate-in animate-delay-1">
                <span className="hero-exclusive-badge">
                  <i className="bi bi-stars text-warning me-1"></i>
                  Next-Gen Beauty Intelligence
                </span>
              </div>

              <h1 className="luxury-hero-title animate-in animate-delay-2">
                Discover Beauty That{' '}
                <span className="gradient-text">Actually Matches</span> Your Skin.
              </h1>

              <p className="luxury-hero-subtitle animate-in animate-delay-3">
                No more guesswork or mismatched routines. Explore scientifically curated skincare, haircare, and cosmetics with complete ingredient transparency and tailored smart recommendations.
              </p>

              {/* Hero Fast Search Bar */}
              <form onSubmit={handleHeroSearch} className="hero-search-box animate-in animate-delay-4">
                <i className="bi bi-search hero-search-icon"></i>
                <input
                  type="text"
                  placeholder="Search by ingredient, skin concern, or category..."
                  value={heroSearch}
                  onChange={(e) => setHeroSearch(e.target.value)}
                  className="hero-search-field"
                />
                <button type="submit" className="btn-glow hero-search-btn">
                  Explore <i className="bi bi-arrow-right"></i>
                </button>
              </form>

              {/* Quick Tags */}
              <div className="hero-quick-tags animate-in animate-delay-4">
                <span className="quick-tag-label">Trending Now:</span>
                <Link to="/products?concern=brightening" className="quick-tag">✨ Vitamin C</Link>
                <Link to="/products?concern=acne" className="quick-tag">🌿 Niacinamide</Link>
                <Link to="/products?skin_type=dry" className="quick-tag">💧 Hyaluronic</Link>
                <Link to="/products?category=fragrance" className="quick-tag">🌸 Parfums</Link>
              </div>
            </div>

            {/* Hero Visual Glass Showcase */}
            <div className="col-lg-5">
              <div className="hero-visual-container animate-in animate-delay-3">
                <div className="hero-main-card glass-card">
                  <div className="hero-card-header">
                    <div className="hero-card-brand">
                      <span className="dot-live"></span>
                      <span>SMART MATCH ENGINE</span>
                    </div>
                    <span className="badge-pill-glow badge-violet">99.4% Match</span>
                  </div>

                  <div className="hero-featured-image-box">
                    <img
                      src="https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=600&q=80"
                      alt="Featured Beauty"
                      className="hero-featured-img"
                    />
                    <div className="hero-img-badge">
                      <i className="bi bi-award-fill text-warning me-1"></i>
                      #1 Recommended Serum
                    </div>
                  </div>

                  <div className="hero-card-info">
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <h4 className="hero-prod-title">Radiance Vitamin C Serum</h4>
                        <p className="hero-prod-sub">Ascorbic Acid 15% + Hyaluronic Acid</p>
                      </div>
                      <span className="hero-prod-price">₹764</span>
                    </div>

                    <div className="hero-stats-row">
                      <div className="hero-stat-item">
                        <span className="stat-label">Skin Compatibility</span>
                        <span className="stat-val text-success">✦ All Types</span>
                      </div>
                      <div className="hero-stat-item">
                        <span className="stat-label">Rating</span>
                        <span className="stat-val text-warning">★ 4.6 (342)</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Floating Micro Cards */}
                <div className="hero-floating-badge badge-top-right glass-card">
                  <i className="bi bi-shield-check text-success fs-5"></i>
                  <div>
                    <div className="fw-bold fs-7">Clean Actives</div>
                    <div className="text-muted fs-8">100% Verified INCI</div>
                  </div>
                </div>

                <div className="hero-floating-badge badge-bottom-left glass-card">
                  <i className="bi bi-lightning-charge-fill text-warning fs-5"></i>
                  <div>
                    <div className="fw-bold fs-7">Instant SmartMatch</div>
                    <div className="text-muted fs-8">Personalized to You</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Category Quick Grid ──────────────────────────────── */}
      <section className="categories-section">
        <div className="container">
          <div className="section-head-center">
            <span className="badge-pill-glow badge-violet mb-2">
              <i className="bi bi-grid-3x3-gap me-1"></i> Curated Collections
            </span>
            <h2 className="section-main-heading">Shop By Category</h2>
            <p className="section-main-sub">Explore formulas tailored to every step of your self-care routine</p>
          </div>

          <div className="row g-3 g-md-4">
            {CATEGORIES.map((cat) => (
              <div className="col-6 col-md-4 col-lg-2" key={cat.id}>
                <Link to={`/products?category=${cat.id}`} className="category-card-link">
                  <div className="category-tile glass-card">
                    <div className="category-icon-box" style={{ background: `rgba(${cat.id === 'skincare' ? '124, 92, 252' : cat.id === 'makeup' ? '255, 77, 109' : cat.id === 'haircare' ? '56, 189, 248' : cat.id === 'fragrance' ? '168, 85, 247' : cat.id === 'bodycare' ? '251, 146, 60' : '236, 72, 153'}, 0.15)` }}>
                      <i className={`bi ${cat.icon}`} style={{ color: cat.color }}></i>
                    </div>
                    <h5 className="category-name">{cat.name}</h5>
                    <span className="category-desc">{cat.desc}</span>
                  </div>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Bestsellers Section ──────────────────────────────── */}
      <section className="showcase-section">
        <div className="container">
          <div className="d-flex flex-wrap align-items-end justify-content-between mb-4 gap-3">
            <div>
              <span className="badge-pill-glow badge-rose mb-2">
                <i className="bi bi-fire me-1"></i> Customer Favorites
              </span>
              <h2 className="section-main-heading mb-0">Trending Bestsellers</h2>
            </div>
            <Link to="/products?bestseller=true" className="btn-glass">
              View All Bestsellers <i className="bi bi-arrow-right ms-1"></i>
            </Link>
          </div>

          {loading ? (
            <LoadingState message="Loading bestsellers..." />
          ) : error ? (
            <ErrorState message={error} onRetry={loadFeatured} />
          ) : (
            <div className="row g-4">
              {bestsellers.slice(0, 4).map((product) => (
                <div className="col-6 col-md-4 col-lg-3" key={product.id}>
                  <ProductCard product={product} />
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* ── Beauty Intelligence Value Props ─────────────────── */}
      <section className="features-section">
        <div className="container">
          <div className="feature-banner-box glass-card">
            <div className="row align-items-center gy-4">
              <div className="col-lg-4 text-center text-lg-start p-lg-4">
                <span className="badge-pill-glow badge-violet mb-2">
                  <i className="bi bi-cpu me-1"></i> The SmartMatch Difference
                </span>
                <h3 className="feature-highlight-title">Why Shoppers Trust Joyory SmartMatch</h3>
                <p className="text-muted-custom">We combine formulation science with rule-based matching so you get results you can see and feel.</p>
                <Link to="/quiz" className="btn-glow mt-2">
                  <i className="bi bi-magic me-1"></i> Start Matching Quiz
                </Link>
              </div>

              <div className="col-lg-8">
                <div className="row g-3">
                  {[
                    {
                      icon: 'bi-droplet-half',
                      title: '100% INCI Transparency',
                      desc: 'Full breakdown of key actives, percentages, and formulations for every product.',
                      color: 'var(--sm-primary-light)',
                      bg: 'rgba(124, 92, 252, 0.12)',
                    },
                    {
                      icon: 'bi-person-check',
                      title: 'Skin-Type Compatibility',
                      desc: 'Filter directly by Oily, Dry, Combination, or Sensitive skin needs with instant tags.',
                      color: 'var(--sm-accent)',
                      bg: 'rgba(255, 77, 109, 0.12)',
                    },
                    {
                      icon: 'bi-shield-exclamation',
                      title: 'Dermatology & Cautions',
                      desc: 'Know how to layer actives safely with explicit caution notices and usage routines.',
                      color: 'var(--sm-gold)',
                      bg: 'rgba(245, 158, 11, 0.12)',
                    },
                    {
                      icon: 'bi-cash-coin',
                      title: 'Fair & Transparent Pricing',
                      desc: 'Real discounts and honest pricing without hidden markups or misleading claims.',
                      color: 'var(--sm-success-light)',
                      bg: 'rgba(16, 185, 129, 0.12)',
                    },
                  ].map((item, idx) => (
                    <div className="col-md-6" key={idx}>
                      <div className="feature-mini-card">
                        <div className="feature-icon-wrapper" style={{ background: item.bg, color: item.color }}>
                          <i className={`bi ${item.icon}`}></i>
                        </div>
                        <div>
                          <h5 className="feature-mini-title">{item.title}</h5>
                          <p className="feature-mini-desc">{item.desc}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── New Arrivals Section ─────────────────────────────── */}
      {newArrivals.length > 0 && (
        <section className="showcase-section">
          <div className="container">
            <div className="d-flex flex-wrap align-items-end justify-content-between mb-4 gap-3">
              <div>
                <span className="badge-pill-glow badge-emerald mb-2">
                  <i className="bi bi-sparkle me-1"></i> Just Landed
                </span>
                <h2 className="section-main-heading mb-0">Fresh Drops & New In</h2>
              </div>
              <Link to="/products?new=true" className="btn-glass">
                View All New Arrivals <i className="bi bi-arrow-right ms-1"></i>
              </Link>
            </div>

            <div className="row g-4">
              {newArrivals.slice(0, 4).map((product) => (
                <div className="col-6 col-md-4 col-lg-3" key={product.id}>
                  <ProductCard product={product} />
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ── Luxury CTA Banner ────────────────────────────────── */}
      <section className="home-cta-section">
        <div className="container">
          <div className="luxury-cta-banner glass-card text-center p-5 position-relative overflow-hidden">
            <div className="cta-orb cta-orb-1"></div>
            <div className="cta-orb cta-orb-2"></div>
            
            <div className="position-relative z-2 max-w-600 mx-auto">
              <span className="badge-pill-glow badge-rose mb-3">
                <i className="bi bi-stars me-1"></i> Personalized For You
              </span>
              <h2 className="cta-heading">Ready To Upgrade Your Beauty Routine?</h2>
              <p className="cta-sub">
                Explore our full catalog of 12+ meticulously formulated products across skincare, haircare, makeup, and fragrance.
              </p>
              <div className="d-flex flex-wrap justify-content-center gap-3 mt-4">
                <Link to="/products" className="btn-glow btn-lg-custom">
                  <i className="bi bi-bag-heart me-2"></i> Shop Entire Collection
                </Link>
                <Link to="/products?bestseller=true" className="btn-glass btn-lg-custom">
                  <i className="bi bi-fire me-2"></i> Browse Bestsellers
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default HomePage;
