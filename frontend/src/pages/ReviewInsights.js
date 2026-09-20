import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchReviewInsights } from '../services/api';
import { LoadingState, ErrorState } from '../components/StateDisplay';
import './ReviewInsights.css';

const CATEGORY_ICONS = {
  skincare: '🧴', haircare: '💆', makeup: '💄',
  fragrance: '🌸', bodycare: '🛁', nailcare: '💅', tools: '🔧',
};

function StarDisplay({ rating, max = 5 }) {
  const full = Math.floor(rating);
  const half = rating - full >= 0.5;
  return (
    <span className="ri-stars">
      {Array.from({ length: max }).map((_, i) => (
        <i
          key={i}
          className={`bi ${i < full ? 'bi-star-fill' : i === full && half ? 'bi-star-half' : 'bi-star'}`}
        />
      ))}
      <span className="ri-star-val">{rating}</span>
    </span>
  );
}

function ConfidenceBadge({ confidence }) {
  return (
    <span className="ri-confidence-badge" style={{ background: confidence.color + '18', color: confidence.color, border: `1px solid ${confidence.color}40` }}>
      {confidence.label}
    </span>
  );
}

function ReviewInsights() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchReviewInsights()
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="ri-page"><div className="container"><LoadingState message="Analyzing catalog ratings..." /></div></div>;
  if (error) return <div className="ri-page"><div className="container"><ErrorState message={error} /></div></div>;
  if (!data || !data.data_available) return (
    <div className="ri-page">
      <div className="container">
        <div className="ri-empty glass-card">
          <div className="ri-empty-icon">📊</div>
          <h3>No Products Found</h3>
          <p>Add products to the catalog to see rating insights.</p>
        </div>
      </div>
    </div>
  );

  const { catalog_summary: s, rating_distribution, category_breakdown, top_products, confidence_breakdown } = data;

  return (
    <div className="ri-page">
      <div className="container">

        {/* Header */}
        <div className="ri-header glass-card animate-in">
          <div className="ri-header-badge">
            <i className="bi bi-bar-chart-line me-1" />
            Catalog Rating Intelligence
          </div>
          <h1 className="ri-title">
            Review <span className="ri-gradient-text">Insights</span>
          </h1>
          <p className="ri-subtitle">
            Rating analysis across {s.total_products_analyzed} products — {s.total_review_count.toLocaleString()} total customer reviews.
          </p>

          {/* Honest Disclaimer */}
          <div className="ri-disclaimer-banner">
            <i className="bi bi-info-circle-fill me-2" />
            <span>
              <strong>Data transparency:</strong> {data.data_disclaimer}
            </span>
          </div>
        </div>

        {/* Metric Cards */}
        <div className="ri-metrics-grid animate-in">
          <div className="ri-metric-card glass-card">
            <div className="ri-metric-icon">⭐</div>
            <div className="ri-metric-val">{s.average_catalog_rating}</div>
            <div className="ri-metric-label">Avg. Catalog Rating</div>
          </div>
          <div className="ri-metric-card glass-card">
            <div className="ri-metric-icon">📝</div>
            <div className="ri-metric-val">{s.total_review_count.toLocaleString()}</div>
            <div className="ri-metric-label">Total Review Count</div>
          </div>
          <div className="ri-metric-card glass-card">
            <div className="ri-metric-icon">🌟</div>
            <div className="ri-metric-val">{s.products_rated_4_5_plus}</div>
            <div className="ri-metric-label">Products ★4.5+</div>
          </div>
          <div className="ri-metric-card glass-card">
            <div className="ri-metric-icon">📦</div>
            <div className="ri-metric-val">{s.total_products_analyzed}</div>
            <div className="ri-metric-label">Products Analyzed</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="ri-tabs">
          {[
            { id: 'overview', label: '📊 Overview' },
            { id: 'distribution', label: '⭐ Rating Distribution' },
            { id: 'categories', label: '🗂️ By Category' },
            { id: 'top', label: '🏆 Top Products' },
          ].map((tab) => (
            <button
              key={tab.id}
              className={`ri-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
              id={`ri-tab-${tab.id}`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* TAB: Overview */}
        {activeTab === 'overview' && (
          <div className="ri-panel animate-in">
            {/* Rating Distribution mini bars */}
            <div className="ri-overview-dist glass-card">
              <h4 className="ri-section-title">Rating Distribution</h4>
              {rating_distribution.map((band, idx) => (
                <div key={idx} className="ri-dist-row">
                  <span className="ri-dist-emoji">{band.emoji}</span>
                  <div className="ri-dist-bar-wrap">
                    <div className="ri-dist-bar-fill" style={{ width: `${band.percentage}%` }} />
                  </div>
                  <span className="ri-dist-count">{band.count} product{band.count !== 1 ? 's' : ''}</span>
                  <span className="ri-dist-pct">{band.percentage}%</span>
                </div>
              ))}
            </div>

            {/* Confidence Breakdown */}
            <div className="ri-confidence-card glass-card">
              <h4 className="ri-section-title">
                Review Confidence Tiers
                <small className="ms-2 text-muted" style={{ fontSize: '0.72rem', fontWeight: 400 }}>
                  Higher review count = more reliable average rating
                </small>
              </h4>
              {confidence_breakdown.filter(t => t.count > 0).map((tier, idx) => (
                <div key={idx} className="ri-conf-row">
                  <span className="ri-conf-dot" style={{ background: tier.color }} />
                  <span className="ri-conf-label">{tier.tier}</span>
                  <span className="ri-conf-threshold">({tier.threshold})</span>
                  <span className="ri-conf-count">{tier.count} product{tier.count !== 1 ? 's' : ''}</span>
                </div>
              ))}
            </div>

            {/* What's missing note */}
            <div className="ri-missing-card glass-card">
              <h4 className="ri-section-title">
                <i className="bi bi-exclamation-circle me-2 text-warning" />
                What Could Be Added
              </h4>
              <p className="text-muted" style={{ fontSize: '0.88rem' }}>
                {data.what_is_missing}
              </p>
              <div className="ri-future-features">
                {['Sentiment Analysis (positive/negative themes)', 'Review Timeline (trends over time)', 'Photo Reviews', 'Verified Purchase Tags', 'Helpful Votes'].map((f, i) => (
                  <span key={i} className="ri-future-chip">
                    <i className="bi bi-plus me-1" />{f}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB: Distribution */}
        {activeTab === 'distribution' && (
          <div className="ri-panel animate-in">
            {rating_distribution.map((band, idx) => (
              <div key={idx} className="ri-band-card glass-card">
                <div className="ri-band-header">
                  <span className="ri-band-emoji">{band.emoji}</span>
                  <span className="ri-band-label">{band.band}</span>
                  <span className="ri-band-count">{band.count} product{band.count !== 1 ? 's' : ''}</span>
                </div>
                {band.products.length > 0 ? (
                  <div className="ri-band-products">
                    {band.products.map((p) => (
                      <Link key={p.id} to={`/products/${p.id}`} className="ri-band-product">
                        <span className="ri-band-pname">{p.name}</span>
                        <span className="ri-band-prating">★ {p.rating}</span>
                        <span className="ri-band-prev">({p.review_count} reviews)</span>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <p className="ri-band-empty">No products in this rating band.</p>
                )}
              </div>
            ))}
          </div>
        )}

        {/* TAB: Categories */}
        {activeTab === 'categories' && (
          <div className="ri-panel animate-in">
            {category_breakdown.map((cat, idx) => (
              <div key={idx} className="ri-cat-card glass-card">
                <div className="ri-cat-header">
                  <span className="ri-cat-icon">{CATEGORY_ICONS[cat.category] || '📦'}</span>
                  <div>
                    <div className="ri-cat-name">{cat.category.charAt(0).toUpperCase() + cat.category.slice(1)}</div>
                    <div className="ri-cat-meta">{cat.product_count} product{cat.product_count !== 1 ? 's' : ''} · {cat.total_reviews.toLocaleString()} reviews</div>
                  </div>
                  <div className="ri-cat-right">
                    <StarDisplay rating={cat.average_rating} />
                    <ConfidenceBadge confidence={cat.confidence} />
                  </div>
                </div>
                <div className="ri-cat-best">
                  <i className="bi bi-trophy me-1 text-warning" />
                  Best rated: <Link to={`/products/${cat.best_rated_product.id}`} className="ri-cat-link">
                    {cat.best_rated_product.name}
                  </Link> — ★{cat.best_rated_product.rating}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* TAB: Top Products */}
        {activeTab === 'top' && (
          <div className="ri-panel animate-in">
            {[
              { title: '🌟 Top Rated Products', key: 'top_rated', subtitle: 'Sorted by rating, then review count' },
              { title: '📝 Most Reviewed Products', key: 'most_reviewed', subtitle: 'Products with the highest review volume' },
              { title: '💰 Best Value Products', key: 'best_value', subtitle: 'Rating-to-price ratio (higher = more value per rupee)' },
            ].map(({ title, key, subtitle }) => (
              <div key={key} className="ri-top-section glass-card">
                <h4 className="ri-section-title">{title}</h4>
                <p className="ri-top-subtitle">{subtitle}</p>
                {top_products[key].map((p, idx) => (
                  <Link key={p.id} to={`/products/${p.id}`} className="ri-top-item">
                    <div className="ri-top-rank">#{idx + 1}</div>
                    <div className="ri-top-info">
                      <div className="ri-top-name">{p.name}</div>
                      <div className="ri-top-brand">{p.brand} · {p.category}</div>
                    </div>
                    <div className="ri-top-stats">
                      <div className="ri-top-rating">★ {p.rating}</div>
                      <div className="ri-top-revcount">{p.review_count.toLocaleString()} reviews</div>
                      <ConfidenceBadge confidence={p.confidence} />
                    </div>
                  </Link>
                ))}
              </div>
            ))}
          </div>
        )}

        {/* CTA */}
        <div className="ri-cta">
          <Link to="/quiz" className="btn-glow">
            <i className="bi bi-magic me-2" />Find Your Match
          </Link>
          <Link to="/products" className="btn-glass">
            <i className="bi bi-grid me-2" />Browse All Products
          </Link>
        </div>

      </div>
    </div>
  );
}

export default ReviewInsights;
