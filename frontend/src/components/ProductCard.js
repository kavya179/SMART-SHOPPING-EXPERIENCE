import React from 'react';
import { Link } from 'react-router-dom';
import { useShop } from '../context/ShopContext';
import './ProductCard.css';

/**
 * Category display labels with icons
 */
const CATEGORY_META = {
  skincare: { label: 'Skincare', icon: 'bi-droplet' },
  haircare: { label: 'Haircare', icon: 'bi-scissors' },
  makeup: { label: 'Makeup', icon: 'bi-brush' },
  fragrance: { label: 'Fragrance', icon: 'bi-flower1' },
  bodycare: { label: 'Body Care', icon: 'bi-heart-pulse' },
  nailcare: { label: 'Nail Care', icon: 'bi-palette' },
  tools: { label: 'Tools', icon: 'bi-gear' },
};

/**
 * Luxury Product Card Component
 */
function ProductCard({ product }) {
  const { isInWishlist, toggleWishlist, isInCompare, toggleCompare, addToCart } = useShop();

  const {
    id,
    name,
    brand,
    category,
    price,
    discount_percent,
    discounted_price,
    rating,
    review_count,
    image_url,
    skin_type,
    key_ingredients,
    is_bestseller,
    is_new_arrival,
  } = product;

  const hasDiscount = discount_percent > 0;
  const catInfo = CATEGORY_META[category] || { label: category, icon: 'bi-tag' };
  const inWishlist = isInWishlist(id);
  const inCompare = isInCompare(id);

  // Get primary active ingredient if available
  const primaryIngredient = key_ingredients ? key_ingredients.split(',')[0].trim() : null;

  const handleWishlistClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    toggleWishlist(product);
  };

  const handleCompareClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    toggleCompare(product);
  };

  const handleQuickAdd = (e) => {
    e.preventDefault();
    e.stopPropagation();
    addToCart(product);
  };

  return (
    <div className="product-card-wrap">
      <div className="luxury-product-card glass-card h-100">
        {/* Floating Quick Action Buttons */}
        <div className="card-top-actions">
          <button
            className={`card-action-btn btn-wishlist ${inWishlist ? 'active' : ''}`}
            onClick={handleWishlistClick}
            title={inWishlist ? 'Remove from wishlist' : 'Add to wishlist'}
            aria-label="Wishlist"
          >
            <i className={`bi ${inWishlist ? 'bi-heart-fill text-danger' : 'bi-heart'}`}></i>
          </button>
          <button
            className={`card-action-btn btn-compare ${inCompare ? 'active' : ''}`}
            onClick={handleCompareClick}
            title={inCompare ? 'Remove from compare' : 'Add to compare'}
            aria-label="Compare"
          >
            <i className={`bi ${inCompare ? 'bi-check-circle-fill text-primary-light' : 'bi-intersect'}`}></i>
          </button>
        </div>

        <Link to={`/products/${id}`} className="product-card-link" aria-label={`View ${name}`}>
          {/* Image & Badges */}
          <div className="card-media-wrapper">
            <div className="card-badge-container">
              {is_bestseller && (
                <span className="card-pill-badge pill-bestseller">
                  <i className="bi bi-fire"></i> Bestseller
                </span>
              )}
              {is_new_arrival && (
                <span className="card-pill-badge pill-new">
                  <i className="bi bi-sparkle"></i> New
                </span>
              )}
              {hasDiscount && (
                <span className="card-pill-badge pill-discount">
                  -{discount_percent}%
                </span>
              )}
            </div>

            <div className="card-rating-float">
              <i className="bi bi-star-fill text-warning"></i>
              <span>{rating}</span>
              {review_count && <span className="rating-count">({review_count})</span>}
            </div>

            <div className="card-img-container">
              <img
                src={image_url || 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=600&q=80'}
                alt={name}
                className="luxury-card-img"
                loading="lazy"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80';
                }}
              />
              <div className="card-hover-overlay">
                <button type="button" className="btn-quick-add" onClick={handleQuickAdd}>
                  <i className="bi bi-bag-plus me-1"></i> Quick Add
                </button>
                <span className="btn-quick-view">
                  Explore <i className="bi bi-arrow-right ms-1"></i>
                </span>
              </div>
            </div>
          </div>

          {/* Product Details */}
          <div className="luxury-card-body">
            <div className="card-meta-line">
              <span className="card-cat-label">
                <i className={`bi ${catInfo.icon} me-1`}></i>
                {catInfo.label}
              </span>
              {skin_type && skin_type !== 'all' && (
                <span className="card-skin-badge">{skin_type} skin</span>
              )}
            </div>

            <h5 className="luxury-card-title">{name}</h5>
            <p className="luxury-card-brand">{brand}</p>

            {primaryIngredient && (
              <div className="card-actives-tag">
                <i className="bi bi-shield-check me-1"></i>
                <span className="text-truncate">{primaryIngredient}</span>
              </div>
            )}

            <div className="luxury-card-footer">
              <div className="price-stack">
                <span className="price-current">₹{discounted_price || price}</span>
                {hasDiscount && (
                  <span className="price-slashed">₹{price}</span>
                )}
              </div>
              <span className="view-link-text">
                <i className="bi bi-chevron-right"></i>
              </span>
            </div>
          </div>
        </Link>
      </div>
    </div>
  );
}

export default ProductCard;
