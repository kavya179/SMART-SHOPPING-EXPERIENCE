import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { fetchProducts, fetchCategories } from '../services/api';
import ProductCard from '../components/ProductCard';
import { LoadingState, ErrorState } from '../components/StateDisplay';
import './ProductCatalog.css';

const SKIN_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'oily', label: 'Oily' },
  { value: 'dry', label: 'Dry' },
  { value: 'combination', label: 'Combination' },
  { value: 'sensitive', label: 'Sensitive' },
  { value: 'normal', label: 'Normal' },
];

const CONCERN_PRESETS = [
  { value: '', label: 'All Concerns' },
  { value: 'brightening', label: '✨ Brightening' },
  { value: 'acne', label: '🌿 Acne & Pores' },
  { value: 'hydration', label: '💧 Hydration' },
  { value: 'frizz', label: '💆‍♀️ Frizz & Hairfall' },
  { value: 'long-lasting', label: '💄 Long-Lasting' },
];

const PRICE_PRESETS = [
  { label: 'All', min: '', max: '' },
  { label: 'Under ₹500', min: '', max: '500' },
  { label: '₹500 - ₹900', min: '500', max: '900' },
  { label: '₹900+', min: '900', max: '' },
];

const SORT_OPTIONS = [
  { value: '', label: '✨ Recommended' },
  { value: '-rating', label: '★ Highest Rated' },
  { value: 'price', label: 'Price: Low → High' },
  { value: '-price', label: 'Price: High → Low' },
  { value: 'name', label: 'Alphabetical: A → Z' },
];

function ProductCatalog() {
  const [searchParams, setSearchParams] = useSearchParams();

  // ── State ─────────────────────────────────────────────────
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ── Filters (initialized from URL params) ─────────────────
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [category, setCategory] = useState(searchParams.get('category') || '');
  const [skinType, setSkinType] = useState(searchParams.get('skin_type') || '');
  const [concern, setConcern] = useState(searchParams.get('concern') || '');
  const [minPrice, setMinPrice] = useState(searchParams.get('min_price') || '');
  const [maxPrice, setMaxPrice] = useState(searchParams.get('max_price') || '');
  const [ordering, setOrdering] = useState(searchParams.get('ordering') || '');
  const [showBestsellers, setShowBestsellers] = useState(searchParams.get('bestseller') === 'true');
  const [showNew, setShowNew] = useState(searchParams.get('new') === 'true');

  // ── Debounced search term ─────────────────────────────────
  const [debouncedSearch, setDebouncedSearch] = useState(search);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 350);
    return () => clearTimeout(timer);
  }, [search]);

  // Keep state synced if URL params change from outside (e.g. navbar click)
  useEffect(() => {
    setSearch(searchParams.get('search') || '');
    setCategory(searchParams.get('category') || '');
    setSkinType(searchParams.get('skin_type') || '');
    setConcern(searchParams.get('concern') || '');
    setMinPrice(searchParams.get('min_price') || '');
    setMaxPrice(searchParams.get('max_price') || '');
    setOrdering(searchParams.get('ordering') || '');
    setShowBestsellers(searchParams.get('bestseller') === 'true');
    setShowNew(searchParams.get('new') === 'true');
  }, [searchParams]);

  // ── Load categories once ──────────────────────────────────
  useEffect(() => {
    fetchCategories()
      .then(setCategories)
      .catch(() => {});
  }, []);

  // ── Build filters object ──────────────────────────────────
  const buildFilters = useCallback(() => {
    const filters = {};
    if (debouncedSearch) filters.search = debouncedSearch;
    if (category) filters.category = category;
    if (skinType) filters.skin_type = skinType;
    if (concern) filters.concern = concern;
    if (minPrice) filters.min_price = minPrice;
    if (maxPrice) filters.max_price = maxPrice;
    if (ordering) filters.ordering = ordering;
    if (showBestsellers) filters.bestseller = 'true';
    if (showNew) filters.new = 'true';
    return filters;
  }, [debouncedSearch, category, skinType, concern, minPrice, maxPrice, ordering, showBestsellers, showNew]);

  // ── Fetch products ────────────────────────────────────────
  const loadProducts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const filters = buildFilters();
      const data = await fetchProducts(filters);
      setProducts(data.results || []);
      setTotalCount(data.count || 0);

      // Sync URL params
      const params = {};
      Object.entries(filters).forEach(([k, v]) => {
        if (v) params[k] = v;
      });
      setSearchParams(params, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [buildFilters, setSearchParams]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  // ── Clear all filters ─────────────────────────────────────
  const clearFilters = () => {
    setSearch('');
    setCategory('');
    setSkinType('');
    setConcern('');
    setMinPrice('');
    setMaxPrice('');
    setOrdering('');
    setShowBestsellers(false);
    setShowNew(false);
  };

  const handlePricePreset = (preset) => {
    setMinPrice(preset.min);
    setMaxPrice(preset.max);
  };

  const hasActiveFilters = Boolean(
    search || category || skinType || concern || minPrice || maxPrice || ordering || showBestsellers || showNew
  );

  return (
    <div className="catalog-page-wrapper">
      <div className="container">
        {/* ── Header Banner ──────────────────────────────────── */}
        <div className="catalog-hero-header glass-card p-4 p-md-5 mb-4">
          <div className="row align-items-center gy-3">
            <div className="col-lg-7">
              <span className="badge-pill-glow badge-violet mb-2">
                <i className="bi bi-grid-fill me-1"></i> Full Product Collection
              </span>
              <h1 className="catalog-main-title">
                Beauty & Personal Care <span className="gradient-text">Catalog</span>
              </h1>
              <p className="catalog-main-sub mb-0">
                Filter by formulation, concern, or skin compatibility to discover products matched for you.
              </p>
            </div>

            {/* Quick Stats */}
            <div className="col-lg-5">
              <div className="catalog-header-stats">
                <div className="cat-stat-card">
                  <span className="stat-number">{totalCount}</span>
                  <span className="stat-desc">Products Available</span>
                </div>
                <div className="cat-stat-card">
                  <span className="stat-number">100%</span>
                  <span className="stat-desc">Clean Transparency</span>
                </div>
                <div className="cat-stat-card">
                  <span className="stat-number">4.6★</span>
                  <span className="stat-desc">Avg Rating</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── Active Filter Bar & Quick Category Chips ────────── */}
        <div className="category-pills-bar mb-4">
          <button
            className={`cat-pill-btn ${category === '' ? 'active' : ''}`}
            onClick={() => setCategory('')}
          >
            All Items
          </button>
          {categories.map((cat) => (
            <button
              key={cat.value}
              className={`cat-pill-btn ${category === cat.value ? 'active' : ''}`}
              onClick={() => setCategory(category === cat.value ? '' : cat.value)}
            >
              {cat.label} <span className="pill-count">{cat.count}</span>
            </button>
          ))}
        </div>

        <div className="row g-4">
          {/* ── Sidebar Filters ─────────────────────────────── */}
          <div className="col-lg-3">
            <aside className="filter-sidebar glass-card p-4">
              <div className="filter-top-bar">
                <h5 className="filter-panel-heading mb-0">
                  <i className="bi bi-sliders me-2 text-primary-light"></i> Refine
                </h5>
                {hasActiveFilters && (
                  <button className="filter-reset-btn" onClick={clearFilters}>
                    <i className="bi bi-arrow-counterclockwise me-1"></i> Reset
                  </button>
                )}
              </div>

              {/* Search Bar */}
              <div className="filter-block">
                <label className="filter-section-title" htmlFor="cat-search">Search Catalog</label>
                <div className="catalog-search-input-wrap">
                  <i className="bi bi-search search-icon"></i>
                  <input
                    id="cat-search"
                    type="text"
                    className="filter-text-input"
                    placeholder="Search name, ingredients..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                  {search && (
                    <button className="search-input-clear" onClick={() => setSearch('')}>
                      <i className="bi bi-x"></i>
                    </button>
                  )}
                </div>
              </div>

              {/* Skin Type Filter */}
              <div className="filter-block">
                <label className="filter-section-title">Skin Type</label>
                <div className="skin-pill-group">
                  {SKIN_TYPES.map((st) => (
                    <button
                      key={st.value}
                      type="button"
                      className={`skin-pill-btn ${skinType === st.value ? 'active' : ''}`}
                      onClick={() => setSkinType(skinType === st.value ? '' : st.value)}
                    >
                      {st.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Target Concern */}
              <div className="filter-block">
                <label className="filter-section-title">Target Concern</label>
                <select
                  className="filter-dropdown-select"
                  value={concern}
                  onChange={(e) => setConcern(e.target.value)}
                >
                  {CONCERN_PRESETS.map((cp) => (
                    <option key={cp.value} value={cp.value}>{cp.label}</option>
                  ))}
                </select>
              </div>

              {/* Price Range Presets */}
              <div className="filter-block">
                <label className="filter-section-title">Price Range</label>
                <div className="price-presets-group">
                  {PRICE_PRESETS.map((p, idx) => {
                    const isSelected = minPrice === p.min && maxPrice === p.max;
                    return (
                      <button
                        key={idx}
                        type="button"
                        className={`price-preset-pill ${isSelected ? 'active' : ''}`}
                        onClick={() => handlePricePreset(p)}
                      >
                        {p.label}
                      </button>
                    );
                  })}
                </div>
                <div className="d-flex align-items-center gap-2 mt-2">
                  <input
                    type="number"
                    className="filter-text-input text-center"
                    placeholder="Min ₹"
                    value={minPrice}
                    onChange={(e) => setMinPrice(e.target.value)}
                  />
                  <span className="text-dim">–</span>
                  <input
                    type="number"
                    className="filter-text-input text-center"
                    placeholder="Max ₹"
                    value={maxPrice}
                    onChange={(e) => setMaxPrice(e.target.value)}
                  />
                </div>
              </div>

              {/* Quick Tags (Bestsellers / New) */}
              <div className="filter-block">
                <label className="filter-section-title">Highlights</label>
                <div className="d-flex flex-column gap-2">
                  <label className="checkbox-custom-label">
                    <input
                      type="checkbox"
                      checked={showBestsellers}
                      onChange={(e) => setShowBestsellers(e.target.checked)}
                    />
                    <span className="checkbox-text">
                      <i className="bi bi-fire text-danger me-1"></i> Bestsellers Only
                    </span>
                  </label>
                  <label className="checkbox-custom-label">
                    <input
                      type="checkbox"
                      checked={showNew}
                      onChange={(e) => setShowNew(e.target.checked)}
                    />
                    <span className="checkbox-text">
                      <i className="bi bi-sparkle text-primary-light me-1"></i> New Drops Only
                    </span>
                  </label>
                </div>
              </div>
            </aside>
          </div>

          {/* ── Main Product Results Grid ────────────────────── */}
          <div className="col-lg-9">
            {/* Top Toolbar */}
            <div className="catalog-toolbar glass-card p-3 mb-4 d-flex flex-wrap align-items-center justify-content-between gap-3">
              <div className="results-summary">
                <span className="results-badge-count">{totalCount}</span>
                <span className="results-text">
                  product{totalCount !== 1 ? 's' : ''} found
                  {category && ` in ${category}`}
                </span>
              </div>

              {/* Sort Selector */}
              <div className="d-flex align-items-center gap-2">
                <span className="sort-label">Sort:</span>
                <select
                  className="filter-sort-select"
                  value={ordering}
                  onChange={(e) => setOrdering(e.target.value)}
                >
                  {SORT_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Grid or Empty/Loading State */}
            {loading ? (
              <LoadingState message="Matching formulas..." />
            ) : error ? (
              <ErrorState message={error} onRetry={loadProducts} />
            ) : products.length === 0 ? (
              <div className="empty-catalog-box glass-card p-5 text-center">
                <div className="empty-icon-circle mb-3">
                  <i className="bi bi-search"></i>
                </div>
                <h4 className="fw-bold mb-2">No matching products found</h4>
                <p className="text-muted mb-4 max-w-400 mx-auto">
                  Try adjusting or clearing your filters to discover more beauty products.
                </p>
                <button className="btn-glow" onClick={clearFilters}>
                  <i className="bi bi-arrow-counterclockwise me-1"></i> Reset All Filters
                </button>
              </div>
            ) : (
              <div className="row g-3 g-md-4">
                {products.map((product) => (
                  <div className="col-6 col-md-4" key={product.id}>
                    <ProductCard product={product} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductCatalog;
