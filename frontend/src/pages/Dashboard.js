import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchProducts, fetchReviewInsights } from '../services/api';
import { useShop } from '../context/ShopContext';
import './Dashboard.css';

const TOOLS = [
  {
    id: 'quiz',
    to: '/quiz',
    icon: '🔮',
    title: 'SmartMatch Quiz',
    description: 'Answer 4 questions and get personalized product recommendations matched to your skin type, concern, and budget.',
    badge: 'AI-Powered',
    badgeColor: 'primary',
    cta: 'Take the Quiz',
  },
  {
    id: 'routine',
    to: '/routine',
    icon: '📅',
    title: 'Routine Builder',
    description: 'Build your complete AM & PM skincare routine using real products from our catalog — ordered step by step.',
    badge: 'Real Products',
    badgeColor: 'emerald',
    cta: 'Build Routine',
  },
  {
    id: 'ingredient-check',
    to: '/ingredient-check',
    icon: '🛡️',
    title: 'Ingredient Checker',
    description: 'Check if your skincare ingredients conflict. Detect high, medium, and low risk interactions instantly.',
    badge: 'Safety Tool',
    badgeColor: 'gold',
    cta: 'Check Safety',
  },
  {
    id: 'compare',
    to: '/compare',
    icon: '⚖️',
    title: 'Product Compare',
    description: 'Compare up to 3 products side by side — ingredients, value score, skin type, and a Best Pick recommendation.',
    badge: 'Smart Analysis',
    badgeColor: 'violet',
    cta: 'Compare Products',
  },
  {
    id: 'reviews',
    to: '/reviews',
    icon: '📊',
    title: 'Review Insights',
    description: 'Explore rating distributions, category trends, and top-rated products across 3,000+ customer reviews.',
    badge: 'Data-Driven',
    badgeColor: 'primary',
    cta: 'View Insights',
  },
  {
    id: 'faq',
    icon: '💬',
    title: 'Beauty FAQ Assistant',
    description: 'Ask questions about any product — ingredients, usage, skin compatibility — and get instant answers from our catalog.',
    badge: 'Always Available',
    badgeColor: 'emerald',
    cta: 'Open Chat →',
    isInPage: true, // triggers FAQ widget open
  },
];

function Dashboard() {
  const [catalogStats, setCatalogStats] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const { cartCount, wishlist, compareList } = useShop();

  useEffect(() => {
    Promise.allSettled([
      fetchProducts(),
      fetchReviewInsights(),
    ]).then(([productsRes, insightsRes]) => {
      if (productsRes.status === 'fulfilled') {
        const d = productsRes.value;
        setCatalogStats({
          total: d.count || 0,
        });
      }
      if (insightsRes.status === 'fulfilled') {
        setInsights(insightsRes.value);
      }
    }).finally(() => setLoading(false));
  }, []);

  const s = insights?.catalog_summary;

  return (
    <div className="db-page">
      <div className="container">

        {/* Hero */}
        <div className="db-hero glass-card animate-in">
          <div className="db-hero-badge">
            <i className="bi bi-stars me-1" />
            Joyory SmartMatch Platform
          </div>
          <h1 className="db-hero-title">
            Your Smart Beauty <span className="db-gradient-text">Dashboard</span>
          </h1>
          <p className="db-hero-sub">
            All your beauty tools in one place — personalized recommendations, routine building,
            ingredient safety, product comparison, and catalog insights.
          </p>
          <div className="db-hero-actions">
            <Link to="/quiz" className="btn-glow db-cta-main">
              <i className="bi bi-magic me-2" />
              Start SmartMatch Quiz
            </Link>
            <Link to="/products" className="btn-glass">
              <i className="bi bi-grid me-2" />
              Browse Catalog
            </Link>
          </div>
        </div>

        {/* Live Stats */}
        <div className="db-stats-row animate-in">
          <div className="db-stat-card glass-card">
            <i className="bi bi-box-seam db-stat-icon" />
            <div className="db-stat-val">{loading ? '…' : (catalogStats?.total || 12)}</div>
            <div className="db-stat-label">Products in Catalog</div>
          </div>
          <div className="db-stat-card glass-card">
            <i className="bi bi-star-fill db-stat-icon text-warning" />
            <div className="db-stat-val">{loading ? '…' : (s?.average_catalog_rating || '—')}</div>
            <div className="db-stat-label">Avg. Catalog Rating</div>
          </div>
          <div className="db-stat-card glass-card">
            <i className="bi bi-chat-dots db-stat-icon" />
            <div className="db-stat-val">{loading ? '…' : (s?.total_review_count?.toLocaleString() || '—')}</div>
            <div className="db-stat-label">Total Customer Reviews</div>
          </div>
          <div className="db-stat-card glass-card">
            <i className="bi bi-heart db-stat-icon text-danger" />
            <div className="db-stat-val">{wishlist.length}</div>
            <div className="db-stat-label">Items in Wishlist</div>
          </div>
          <div className="db-stat-card glass-card">
            <i className="bi bi-bag db-stat-icon" />
            <div className="db-stat-val">{cartCount}</div>
            <div className="db-stat-label">Items in Cart</div>
          </div>
          <div className="db-stat-card glass-card">
            <i className="bi bi-intersect db-stat-icon" />
            <div className="db-stat-val">{compareList.length}</div>
            <div className="db-stat-label">Products Comparing</div>
          </div>
        </div>

        {/* Tools Grid */}
        <div className="db-section">
          <div className="db-section-header">
            <h2 className="db-section-title">Beauty Intelligence Tools</h2>
            <p className="db-section-sub">All tools use real data from our SQLite product catalog — no fabricated results.</p>
          </div>

          <div className="db-tools-grid">
            {TOOLS.map((tool) =>
              tool.isInPage ? (
                <button
                  key={tool.id}
                  id={`dashboard-tool-${tool.id}`}
                  className="db-tool-card glass-card"
                  onClick={() => {
                    const btn = document.getElementById('faq-launcher-btn');
                    if (btn) btn.click();
                  }}
                >
                  <div className="db-tool-icon">{tool.icon}</div>
                  <span className={`db-tool-badge badge-${tool.badgeColor}`}>{tool.badge}</span>
                  <h3 className="db-tool-title">{tool.title}</h3>
                  <p className="db-tool-desc">{tool.description}</p>
                  <span className="db-tool-cta">{tool.cta} <i className="bi bi-arrow-right" /></span>
                </button>
              ) : (
                <Link key={tool.id} to={tool.to} id={`dashboard-tool-${tool.id}`} className="db-tool-card glass-card">
                  <div className="db-tool-icon">{tool.icon}</div>
                  <span className={`db-tool-badge badge-${tool.badgeColor}`}>{tool.badge}</span>
                  <h3 className="db-tool-title">{tool.title}</h3>
                  <p className="db-tool-desc">{tool.description}</p>
                  <span className="db-tool-cta">{tool.cta} <i className="bi bi-arrow-right" /></span>
                </Link>
              )
            )}
          </div>
        </div>

        {/* Quick Stats from Insights */}
        {insights && s && (
          <div className="db-section">
            <div className="db-section-header">
              <h2 className="db-section-title">Catalog Snapshot</h2>
              <p className="db-section-sub">Live data from the product database</p>
            </div>
            <div className="db-insights-grid">
              <div className="db-insight-card glass-card">
                <h4 className="db-insight-title">⭐ Rating Overview</h4>
                <div className="db-insight-rows">
                  <div className="db-insight-row">
                    <span>Avg. Rating</span>
                    <strong>★ {s.average_catalog_rating}</strong>
                  </div>
                  <div className="db-insight-row">
                    <span>Products ★4.5+</span>
                    <strong>{s.products_rated_4_5_plus}</strong>
                  </div>
                  <div className="db-insight-row">
                    <span>Highest Rated</span>
                    <strong>★ {s.highest_rated}</strong>
                  </div>
                </div>
                <Link to="/reviews" className="db-insight-more">View Full Analysis →</Link>
              </div>

              <div className="db-insight-card glass-card">
                <h4 className="db-insight-title">📝 Review Volume</h4>
                <div className="db-insight-rows">
                  <div className="db-insight-row">
                    <span>Total Reviews</span>
                    <strong>{s.total_review_count.toLocaleString()}</strong>
                  </div>
                  <div className="db-insight-row">
                    <span>Most Reviewed</span>
                    <strong>{s.most_reviewed_count.toLocaleString()}</strong>
                  </div>
                  <div className="db-insight-row">
                    <span>Products Analyzed</span>
                    <strong>{s.total_products_analyzed}</strong>
                  </div>
                </div>
                <Link to="/reviews?tab=top" className="db-insight-more">Top Products →</Link>
              </div>

              {insights.category_breakdown && (
                <div className="db-insight-card glass-card">
                  <h4 className="db-insight-title">🗂️ Top Categories</h4>
                  <div className="db-insight-rows">
                    {insights.category_breakdown.slice(0, 3).map((cat) => (
                      <div key={cat.category} className="db-insight-row">
                        <span style={{ textTransform: 'capitalize' }}>{cat.category}</span>
                        <strong>★ {cat.average_rating}</strong>
                      </div>
                    ))}
                  </div>
                  <Link to="/reviews?tab=categories" className="db-insight-more">By Category →</Link>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Quick Links */}
        <div className="db-quick-links glass-card">
          <h3 className="db-ql-title">Quick Navigation</h3>
          <div className="db-ql-grid">
            {[
              { to: '/products', icon: 'bi-grid-3x3-gap', label: 'All Products' },
              { to: '/products?bestseller=true', icon: 'bi-trophy', label: 'Bestsellers' },
              { to: '/products?new=true', icon: 'bi-stars', label: 'New Arrivals' },
              { to: '/wishlist', icon: 'bi-heart', label: 'Wishlist' },
              { to: '/cart', icon: 'bi-bag', label: 'Cart' },
              { to: '/compare', icon: 'bi-intersect', label: 'Compare' },
              { to: '/products?category=skincare', icon: 'bi-droplet', label: 'Skincare' },
              { to: '/products?category=makeup', icon: 'bi-brush', label: 'Makeup' },
              { to: '/products?category=haircare', icon: 'bi-scissors', label: 'Haircare' },
            ].map((link) => (
              <Link key={link.to} to={link.to} className="db-ql-item">
                <i className={`bi ${link.icon}`} />
                <span>{link.label}</span>
              </Link>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}

export default Dashboard;
