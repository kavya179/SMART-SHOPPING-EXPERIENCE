import React from 'react';
import { Link } from 'react-router-dom';
import { useShop } from '../context/ShopContext';
import ProductCard from '../components/ProductCard';
import './WishlistPage.css';

function WishlistPage() {
  const { wishlist, removeFromWishlist, addToCart } = useShop();

  const handleMoveAllToBag = () => {
    wishlist.forEach((product) => {
      addToCart(product);
    });
  };

  return (
    <div className="wishlist-page-wrapper">
      <div className="container">
        {/* Header */}
        <div className="wishlist-header glass-card p-4 p-md-5 mb-4">
          <div className="d-flex flex-wrap align-items-center justify-content-between gap-3">
            <div>
              <span className="badge-pill-glow badge-rose mb-2">
                <i className="bi bi-heart-fill me-1"></i> Saved Favorites
              </span>
              <h1 className="wishlist-title mb-1">
                My Beauty <span className="gradient-text-rose">Wishlist</span>
              </h1>
              <p className="wishlist-sub mb-0">
                {wishlist.length} saved product{wishlist.length !== 1 ? 's' : ''}. Keep track of formulas you're considering.
              </p>
            </div>

            {wishlist.length > 0 && (
              <div className="d-flex gap-2">
                <button className="btn-glow" onClick={handleMoveAllToBag}>
                  <i className="bi bi-bag-check me-1"></i> Move All to Bag
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Local Storage Demo Disclaimer Banner */}
        <div className="wishlist-demo-banner glass-card p-3 mb-4 d-flex align-items-center gap-3">
          <i className="bi bi-info-circle-fill text-primary-light fs-4"></i>
          <div>
            <span className="fw-bold d-block text-white fs-85">Demo Persistence Notice</span>
            <span className="text-muted fs-8">
              Your wishlist is securely persisted in this browser's local storage for evaluation. No account login is required for this hackathon prototype.
            </span>
          </div>
        </div>

        {/* Wishlist Grid or Empty State */}
        {wishlist.length === 0 ? (
          <div className="wishlist-empty-card glass-card p-5 text-center mx-auto mb-5">
            <div className="empty-icon-circle-rose mb-3">
              <i className="bi bi-heart"></i>
            </div>
            <h2 className="fw-bold mb-2">Your Wishlist is Empty</h2>
            <p className="text-muted mb-4 max-w-450 mx-auto">
              Explore our catalog or take the SmartMatch Quiz to discover and save products tailored to your routine.
            </p>
            <div className="d-flex justify-content-center gap-3">
              <Link to="/products" className="btn-glow">
                <i className="bi bi-grid-3x3-gap me-2"></i> Browse Products
              </Link>
              <Link to="/quiz" className="btn-glass">
                <i className="bi bi-magic me-2"></i> Take Match Quiz
              </Link>
            </div>
          </div>
        ) : (
          <div className="row g-4 mb-5">
            {wishlist.map((product) => (
              <div className="col-6 col-md-4 col-lg-3 position-relative" key={product.id}>
                <div className="wishlist-card-wrapper h-100">
                  <ProductCard product={product} />
                  <button
                    className="btn-remove-wishlist"
                    onClick={() => removeFromWishlist(product.id)}
                    title="Remove from wishlist"
                  >
                    <i className="bi bi-trash"></i>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default WishlistPage;
