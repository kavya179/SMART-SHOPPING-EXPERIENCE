import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useShop } from '../context/ShopContext';
import './CompareDock.css';

function CompareDock() {
  const { compareList, removeFromCompare, clearCompare } = useShop();
  const location = useLocation();

  // Don't show dock if no products or if already on the compare page
  if (compareList.length === 0 || location.pathname === '/compare') {
    return null;
  }

  return (
    <div className="compare-dock-container animate-in">
      <div className="container">
        <div className="compare-dock-card glass-card p-3 d-flex flex-wrap align-items-center justify-content-between gap-3">
          <div className="d-flex align-items-center gap-3">
            <div className="dock-badge">
              <i className="bi bi-intersect text-primary-light"></i>
              <span className="fw-bold">{compareList.length}/3</span>
            </div>
            <div className="d-none d-sm-block">
              <h6 className="dock-title mb-0">Compare Formulas</h6>
              <span className="dock-sub text-muted fs-8">Select up to 3 products to compare side by side</span>
            </div>
          </div>

          {/* Product Thumbnails */}
          <div className="d-flex align-items-center gap-2">
            {compareList.map((product) => (
              <div className="dock-item-thumbnail-wrap" key={product.id} title={product.name}>
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="dock-item-thumb"
                />
                <button
                  className="dock-item-remove"
                  onClick={() => removeFromCompare(product.id)}
                  title="Remove from comparison"
                >
                  <i className="bi bi-x"></i>
                </button>
              </div>
            ))}
            {Array.from({ length: 3 - compareList.length }).map((_, idx) => (
              <div className="dock-item-empty" key={idx}>
                <i className="bi bi-plus text-dim"></i>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className="d-flex align-items-center gap-2">
            <button className="btn-glass btn-sm" onClick={clearCompare}>
              Clear
            </button>
            <Link to="/compare" className="btn-glow btn-sm">
              <i className="bi bi-arrow-left-right me-1"></i> Compare ({compareList.length})
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CompareDock;
