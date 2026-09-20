import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchProductById, fetchProducts } from '../services/api';
import ProductCard from '../components/ProductCard';
import { LoadingState, ErrorState } from '../components/StateDisplay';
import { useShop } from '../context/ShopContext';
import './ProductDetail.css';

const CATEGORY_LABELS = {
  skincare: 'Skincare',
  haircare: 'Haircare',
  makeup: 'Makeup',
  fragrance: 'Fragrance',
  bodycare: 'Body Care',
  nailcare: 'Nail Care',
  tools: 'Tools',
};

const SKIN_TYPE_LABELS = {
  all: 'All Skin Types',
  oily: 'Oily & Acne-Prone',
  dry: 'Dry & Dehydrated',
  combination: 'Combination',
  sensitive: 'Sensitive & Reactive',
  normal: 'Normal',
};

function ProductDetail() {
  const { id } = useParams();
  const { addToCart, toggleWishlist, isInWishlist, toggleCompare, isInCompare } = useShop();
  const [product, setProduct] = useState(null);
  const [relatedProducts, setRelatedProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quantity, setQuantity] = useState(1);

  const inWishlist = product ? isInWishlist(product.id) : false;
  const inCompare = product ? isInCompare(product.id) : false;

  const loadProduct = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProductById(id);
      setProduct(data);

      // Fetch related products in same category
      if (data && data.category) {
        const related = await fetchProducts({ category: data.category });
        if (related && related.results) {
          setRelatedProducts(related.results.filter((p) => String(p.id) !== String(id)).slice(0, 4));
        }
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProduct();
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setQuantity(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const handleAddToBag = () => {
    if (product) {
      addToCart(product, quantity);
    }
  };

  if (loading) {
    return (
      <div className="detail-page-wrapper">
        <LoadingState message="Analyzing formula & formulation profile..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="detail-page-wrapper">
        <ErrorState message={error} onRetry={loadProduct} />
      </div>
    );
  }

  if (!product) return null;

  const {
    name, brand, category, description, price, discount_percent,
    discounted_price, rating, review_count, image_url, skin_type,
    concern_list, key_ingredients, full_ingredients,
    usage_instructions, caution_info, availability, is_bestseller,
    is_new_arrival,
  } = product;

  const hasDiscount = discount_percent > 0;
  const categoryLabel = CATEGORY_LABELS[category] || category;
  const skinTypeLabel = SKIN_TYPE_LABELS[skin_type] || skin_type;

  // Split key ingredients into chips if comma separated
  const ingredientChips = key_ingredients
    ? key_ingredients.split(',').map((ing) => ing.trim()).filter(Boolean)
    : [];

  return (
    <div className="detail-page-wrapper">
      <div className="container">
        {/* ── Breadcrumb ──────────────────────────────────── */}
        <nav className="detail-breadcrumb-bar mb-4" aria-label="breadcrumb">
          <Link to="/" className="breadcrumb-nav-link">
            <i className="bi bi-house me-1"></i> Home
          </Link>
          <i className="bi bi-chevron-right breadcrumb-chevron"></i>
          <Link to="/products" className="breadcrumb-nav-link">Shop</Link>
          <i className="bi bi-chevron-right breadcrumb-chevron"></i>
          <Link to={`/products?category=${category}`} className="breadcrumb-nav-link">
            {categoryLabel}
          </Link>
          <i className="bi bi-chevron-right breadcrumb-chevron"></i>
          <span className="breadcrumb-current-name">{name}</span>
        </nav>

        {/* ── Main Product Section ────────────────────────── */}
        <div className="product-showcase-card glass-card p-4 p-lg-5 mb-5">
          <div className="row g-4 g-lg-5 align-items-start">
            {/* Left: Product Image Gallery */}
            <div className="col-lg-5">
              <div className="detail-gallery-container">
                <div className="detail-badges-overlay">
                  {is_bestseller && (
                    <span className="card-pill-badge pill-bestseller">
                      <i className="bi bi-fire"></i> Bestseller
                    </span>
                  )}
                  {is_new_arrival && (
                    <span className="card-pill-badge pill-new">
                      <i className="bi bi-sparkle"></i> New Drop
                    </span>
                  )}
                  {hasDiscount && (
                    <span className="card-pill-badge pill-discount">
                      -{discount_percent}% OFF
                    </span>
                  )}
                </div>

                <div className="detail-image-box">
                  <img
                    src={image_url || 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80'}
                    alt={name}
                    className="detail-hero-image"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80';
                    }}
                  />
                </div>

                {/* Trust Highlights below image */}
                <div className="detail-trust-row mt-3">
                  <div className="trust-pill">
                    <i className="bi bi-shield-check text-success"></i> Authentic
                  </div>
                  <div className="trust-pill">
                    <i className="bi bi-droplet text-primary-light"></i> Clean Actives
                  </div>
                  <div className="trust-pill">
                    <i className="bi bi-heart text-danger"></i> Cruelty-Free
                  </div>
                </div>
              </div>
            </div>

            {/* Right: Product Details & Purchase Block */}
            <div className="col-lg-7">
              <div className="detail-content-box">
                <div className="d-flex align-items-center justify-content-between mb-2">
                  <span className="badge-pill-glow badge-violet">
                    {categoryLabel}
                  </span>
                  <div className="stock-status-pill">
                    <span className="stock-dot"></span>
                    <span>{availability === 'in_stock' ? 'In Stock & Ready to Ship' : 'Limited Inventory'}</span>
                  </div>
                </div>

                <h1 className="detail-product-title">{name}</h1>
                <div className="detail-brand-badge mb-3">
                  by <span className="brand-highlight">{brand}</span>
                  <i className="bi bi-patch-check-fill text-primary-light ms-1" title="Verified Brand"></i>
                </div>

                {/* Rating Bar */}
                <div className="detail-rating-container mb-3">
                  <div className="stars-wrapper">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <i
                        key={star}
                        className={`bi ${star <= Math.round(rating) ? 'bi-star-fill text-warning' : 'bi-star text-dim'}`}
                      ></i>
                    ))}
                  </div>
                  <span className="detail-rating-score">{rating}</span>
                  <span className="detail-reviews-count">({review_count} verified beauty reviews)</span>
                </div>

                {/* Price Block */}
                <div className="detail-price-panel p-3 mb-4">
                  <div className="d-flex align-items-baseline gap-3">
                    <span className="detail-price-main">₹{discounted_price || price}</span>
                    {hasDiscount && (
                      <>
                        <span className="detail-price-crossed">₹{price}</span>
                        <span className="badge-pill-glow badge-emerald">Save ₹{(price - discounted_price).toFixed(0)}</span>
                      </>
                    )}
                  </div>
                  <span className="tax-included-note">Inclusive of all taxes • Free shipping on orders over ₹499</span>
                </div>

                {/* Description */}
                {description && (
                  <p className="detail-description-text mb-4">{description}</p>
                )}

                {/* SmartMatch Insight Card */}
                <div className="smartmatch-insight-box p-3 mb-4">
                  <div className="insight-header mb-2">
                    <i className="bi bi-stars text-warning me-1"></i>
                    <span className="fw-bold">SmartMatch Formulation Profile</span>
                  </div>
                  <div className="insight-grid">
                    <div>
                      <span className="insight-lbl">Skin Compatibility</span>
                      <span className="insight-val text-primary-light">
                        <i className="bi bi-droplet-half me-1"></i> {skinTypeLabel}
                      </span>
                    </div>
                    <div>
                      <span className="insight-lbl">Primary Actives</span>
                      <span className="insight-val text-success">
                        <i className="bi bi-check2-circle me-1"></i> {ingredientChips[0] || 'Clean Actives'}
                      </span>
                    </div>
                  </div>

                  {concern_list && concern_list.length > 0 && (
                    <div className="mt-3 pt-2 border-top border-secondary-subtle">
                      <span className="insight-lbl d-block mb-1">Target Concerns:</span>
                      <div className="d-flex flex-wrap gap-2">
                        {concern_list.map((c, idx) => (
                          <Link key={idx} to={`/products?concern=${c}`} className="concern-link-chip">
                            #{c}
                          </Link>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="detail-actions-row d-flex flex-wrap align-items-center gap-3 mb-3">
                  <div className="detail-qty-picker d-flex align-items-center">
                    <button
                      className="btn-qty-step"
                      onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                    >
                      <i className="bi bi-dash"></i>
                    </button>
                    <span className="qty-picker-val">{quantity}</span>
                    <button
                      className="btn-qty-step"
                      onClick={() => setQuantity((q) => q + 1)}
                    >
                      <i className="bi bi-plus"></i>
                    </button>
                  </div>

                  <button
                    className="btn-glow btn-lg flex-grow-1"
                    onClick={handleAddToBag}
                  >
                    <i className="bi bi-bag-plus me-2"></i> Add to Beauty Bag
                  </button>
                </div>

                <div className="d-flex flex-wrap gap-2">
                  <button
                    className={`btn-glass btn-sm ${inWishlist ? 'text-danger' : ''}`}
                    onClick={() => toggleWishlist(product)}
                  >
                    <i className={`bi ${inWishlist ? 'bi-heart-fill text-danger' : 'bi-heart'} me-1`}></i>
                    {inWishlist ? 'Saved in Wishlist' : 'Add to Wishlist'}
                  </button>

                  <button
                    className={`btn-glass btn-sm ${inCompare ? 'text-primary-light' : ''}`}
                    onClick={() => toggleCompare(product)}
                  >
                    <i className={`bi ${inCompare ? 'bi-check-circle-fill text-primary-light' : 'bi-intersect'} me-1`}></i>
                    {inCompare ? 'In Comparison' : 'Compare Formula'}
                  </button>

                  <Link to={`/products?category=${category}`} className="btn-glass btn-sm">
                    <i className="bi bi-grid me-1"></i> Similar in {categoryLabel}
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── Formulation & Usage Deep Dive Grid ───────────── */}
        <div className="detail-deepdive-section mb-5">
          <div className="section-head-center mb-4 text-start">
            <span className="badge-pill-glow badge-violet mb-2">
              <i className="bi bi-file-earmark-medical me-1"></i> Scientific Transparency
            </span>
            <h2 className="section-main-heading">Formulation & Routine Guide</h2>
          </div>

          <div className="row g-4">
            {/* Key Actives & Full INCI */}
            <div className="col-lg-6">
              <div className="detail-info-panel glass-card p-4 h-100">
                <div className="panel-title-bar mb-3">
                  <div className="panel-icon-circle bg-violet-soft">
                    <i className="bi bi-capsule text-primary-light"></i>
                  </div>
                  <div>
                    <h4 className="panel-heading mb-0">Ingredients & Actives</h4>
                    <span className="panel-sub">Verified clean formulation list</span>
                  </div>
                </div>

                {ingredientChips.length > 0 && (
                  <div className="mb-4">
                    <span className="info-subhead d-block mb-2">Key Active Ingredients</span>
                    <div className="d-flex flex-wrap gap-2">
                      {ingredientChips.map((chip, idx) => (
                        <span key={idx} className="active-ingredient-chip">
                          <i className="bi bi-check-circle-fill text-success me-1"></i>
                          {chip}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {full_ingredients && (
                  <div>
                    <span className="info-subhead d-block mb-2">Full INCI Formulation</span>
                    <div className="full-inci-box p-3">
                      <p className="full-inci-text mb-0">{full_ingredients}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* How to Use & Routine Steps */}
            <div className="col-lg-6">
              <div className="detail-info-panel glass-card p-4 h-100 d-flex flex-column justify-content-between">
                <div>
                  <div className="panel-title-bar mb-3">
                    <div className="panel-icon-circle bg-emerald-soft">
                      <i className="bi bi-journal-check text-success"></i>
                    </div>
                    <div>
                      <h4 className="panel-heading mb-0">How To Apply & Routine</h4>
                      <span className="panel-sub">Optimal layering guidance</span>
                    </div>
                  </div>

                  {usage_instructions && (
                    <div className="usage-guide-card p-3 mb-3">
                      <p className="usage-text mb-0">
                        <i className="bi bi-sun-fill text-warning me-2"></i>
                        {usage_instructions}
                      </p>
                    </div>
                  )}

                  {/* Caution Box */}
                  {caution_info && (
                    <div className="caution-alert-box p-3">
                      <div className="d-flex align-items-start gap-2">
                        <i className="bi bi-exclamation-triangle-fill text-warning fs-5"></i>
                        <div>
                          <h6 className="fw-bold text-warning mb-1">Dermatology Advisory & Cautions</h6>
                          <p className="caution-text mb-0">{caution_info}</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="patch-test-note mt-3 pt-3 border-top border-secondary-subtle">
                  <i className="bi bi-info-circle me-1 text-primary-light"></i>
                  <span>Always perform a patch test 24 hours prior to regular use on new skincare actives.</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── Related Products Carousel / Grid ───────────────── */}
        {relatedProducts.length > 0 && (
          <section className="related-products-section mb-5">
            <div className="d-flex align-items-center justify-content-between mb-4">
              <div>
                <span className="badge-pill-glow badge-rose mb-1">
                  <i className="bi bi-sparkle me-1"></i> More from {categoryLabel}
                </span>
                <h3 className="section-main-heading mb-0">You May Also Love</h3>
              </div>
              <Link to={`/products?category=${category}`} className="btn-glass">
                View All {categoryLabel} <i className="bi bi-arrow-right ms-1"></i>
              </Link>
            </div>

            <div className="row g-4">
              {relatedProducts.map((relProduct) => (
                <div className="col-6 col-md-4 col-lg-3" key={relProduct.id}>
                  <ProductCard product={relProduct} />
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

export default ProductDetail;
