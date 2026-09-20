import React from 'react';
import { Link } from 'react-router-dom';
import { useShop } from '../context/ShopContext';
import './ComparePage.css';

function ComparePage() {
  const { compareList, removeFromCompare, clearCompare, addToCart, isInWishlist, toggleWishlist } = useShop();

  if (compareList.length === 0) {
    return (
      <div className="compare-page-wrapper">
        <div className="container">
          <div className="compare-empty-card glass-card p-5 text-center mx-auto">
            <div className="empty-icon-circle mb-3">
              <i className="bi bi-intersect"></i>
            </div>
            <span className="badge-pill-glow badge-violet mb-2">Formula Comparison Studio</span>
            <h2 className="fw-bold mb-2">No Products Selected for Comparison</h2>
            <p className="text-muted mb-4 max-w-500 mx-auto">
              Select 2 to 3 beauty products from our catalog to compare active ingredients, skin type suitability, pricing, and formulations side by side.
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
        </div>
      </div>
    );
  }

  return (
    <div className="compare-page-wrapper">
      <div className="container">
        {/* Header */}
        <div className="compare-header glass-card p-4 p-md-5 mb-4">
          <div className="d-flex flex-wrap align-items-center justify-content-between gap-3">
            <div>
              <span className="badge-pill-glow badge-violet mb-2">
                <i className="bi bi-intersect me-1"></i> Side-by-Side Evaluation
              </span>
              <h1 className="compare-page-title mb-1">
                Formulation <span className="gradient-text">Comparison</span>
              </h1>
              <p className="compare-page-sub mb-0">
                Comparing {compareList.length} of 3 selected products. Evaluate ingredients, skin compatibility, and usage instructions side by side.
              </p>
            </div>
            <div className="d-flex gap-2">
              <Link to="/products" className="btn-glass">
                <i className="bi bi-plus-circle me-1"></i> Add More
              </Link>
              <button className="btn-glass" onClick={clearCompare}>
                <i className="bi bi-trash me-1"></i> Clear All
              </button>
            </div>
          </div>
        </div>

        {compareList.length < 2 && (
          <div className="alert-compare-hint glass-card p-3 mb-4 d-flex align-items-center justify-content-between gap-3">
            <div className="d-flex align-items-center gap-2 text-warning">
              <i className="bi bi-info-circle-fill fs-5"></i>
              <span className="fs-9">
                You have selected 1 product. Add at least 1 more product from the catalog to see side-by-side differences!
              </span>
            </div>
            <Link to="/products" className="btn-glow btn-sm">
              + Choose Second Product
            </Link>
          </div>
        )}

        {/* Comparison Matrix Table / Grid */}
        <div className="compare-matrix-card glass-card p-4 overflow-hidden mb-5">
          <div className="table-responsive">
            <table className="table compare-table text-white mb-0">
              <thead>
                <tr>
                  <th className="spec-label-col">Specification</th>
                  {compareList.map((product) => (
                    <th className="product-col" key={product.id}>
                      <div className="compare-prod-head text-center position-relative">
                        <button
                          className="btn-remove-col"
                          onClick={() => removeFromCompare(product.id)}
                          title="Remove from comparison"
                        >
                          <i className="bi bi-x-lg"></i>
                        </button>
                        <div className="compare-prod-img-wrap mx-auto mb-3">
                          <img
                            src={product.image_url}
                            alt={product.name}
                            className="compare-prod-img"
                          />
                        </div>
                        <span className="compare-cat-tag">{product.category}</span>
                        <h5 className="compare-prod-name mb-1">
                          <Link to={`/products/${product.id}`} className="text-white text-decoration-none">
                            {product.name}
                          </Link>
                        </h5>
                        <p className="compare-brand text-muted mb-2">{product.brand}</p>
                        <div className="compare-price-block mb-3">
                          <span className="compare-price-val">₹{product.discounted_price || product.price}</span>
                          {product.discount_percent > 0 && (
                            <span className="compare-price-strike ms-2">₹{product.price}</span>
                          )}
                        </div>
                        <div className="d-flex flex-column gap-2">
                          <button
                            className="btn-glow btn-sm w-100"
                            onClick={() => addToCart(product)}
                          >
                            <i className="bi bi-bag-plus me-1"></i> Add to Bag
                          </button>
                          <button
                            className={`btn-glass btn-sm w-100 ${isInWishlist(product.id) ? 'text-danger' : ''}`}
                            onClick={() => toggleWishlist(product)}
                          >
                            <i className={`bi ${isInWishlist(product.id) ? 'bi-heart-fill text-danger' : 'bi-heart'} me-1`}></i>
                            {isInWishlist(product.id) ? 'Saved' : 'Wishlist'}
                          </button>
                        </div>
                      </div>
                    </th>
                  ))}
                  {Array.from({ length: 3 - compareList.length }).map((_, idx) => (
                    <th className="product-col empty-col" key={idx}>
                      <div className="empty-compare-slot text-center p-4">
                        <div className="slot-icon mb-2">
                          <i className="bi bi-plus-circle-dotted"></i>
                        </div>
                        <h6 className="fw-bold mb-1">Add Another Product</h6>
                        <p className="text-muted fs-8 mb-3">Compare up to 3 formulas</p>
                        <Link to="/products" className="btn-glass btn-sm">
                          Browse Catalog
                        </Link>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {/* Rating */}
                <tr>
                  <td className="spec-label">
                    <i className="bi bi-star-fill text-warning me-2"></i> Rating & Reviews
                  </td>
                  {compareList.map((p) => (
                    <td key={p.id} className="text-center">
                      <span className="fw-bold text-warning">★ {p.rating}</span>
                      <span className="text-muted fs-8 ms-1">({p.review_count || 0} reviews)</span>
                    </td>
                  ))}
                  {Array.from({ length: 3 - compareList.length }).map((_, i) => <td key={i}></td>)}
                </tr>

                {/* Skin Type Compatibility */}
                <tr>
                  <td className="spec-label">
                    <i className="bi bi-person-check text-primary-light me-2"></i> Skin Compatibility
                  </td>
                  {compareList.map((p) => (
                    <td key={p.id} className="text-center">
                      <span className="badge-pill-glow badge-violet">
                        {p.skin_type === 'all' ? 'All Skin Types' : `${p.skin_type} Skin`}
                      </span>
                    </td>
                  ))}
                  {Array.from({ length: 3 - compareList.length }).map((_, i) => <td key={i}></td>)}
                </tr>

                {/* Target Concerns */}
                <tr>
                  <td className="spec-label">
                    <i className="bi bi-target text-danger me-2"></i> Target Concerns
                  </td>
                  {compareList.map((p) => (
                    <td key={p.id} className="text-center">
                      <div className="d-flex flex-wrap justify-content-center gap-1">
                        {p.concern_tags ? (
                          p.concern_tags.split(',').map((tag, tIdx) => (
                            <span key={tIdx} className="diff-chip">
                              {tag.trim()}
                            </span>
                          ))
                        ) : (
                          <span className="text-muted">General care</span>
                        )}
                      </div>
                    </td>
                  ))}
                  {Array.from({ length: 3 - compareList.length }).map((_, i) => <td key={i}></td>)}
                </tr>

                {/* Key Active Ingredients */}
                <tr>
                  <td className="spec-label">
                    <i className="bi bi-capsule text-success me-2"></i> Key Actives
                  </td>
                  {compareList.map((p) => (
                    <td key={p.id}>
                      <p className="spec-text mb-0">{p.key_ingredients || 'Pure formulation'}</p>
                    </td>
                  ))}
                  {Array.from({ length: 3 - compareList.length }).map((_, i) => <td key={i}></td>)}
                </tr>

                {/* Usage Instructions */}
                <tr>
                  <td className="spec-label">
                    <i className="bi bi-journal-text text-primary-light me-2"></i> How to Apply
                  </td>
                  {compareList.map((p) => (
                    <td key={p.id}>
                      <p className="spec-text mb-0 fs-85">{p.usage_instructions || 'Apply as directed on clean skin/hair.'}</p>
                    </td>
                  ))}
                  {Array.from({ length: 3 - compareList.length }).map((_, i) => <td key={i}></td>)}
                </tr>

                {/* Caution / Safety */}
                <tr>
                  <td className="spec-label">
                    <i className="bi bi-shield-exclamation text-warning me-2"></i> Cautions & Notes
                  </td>
                  {compareList.map((p) => (
                    <td key={p.id}>
                      <div className="compare-caution-box p-2">
                        <p className="spec-text mb-0 fs-8 text-warning">{p.caution_info || 'For external use only. Patch test before use.'}</p>
                      </div>
                    </td>
                  ))}
                  {Array.from({ length: 3 - compareList.length }).map((_, i) => <td key={i}></td>)}
                </tr>

                {/* Availability */}
                <tr>
                  <td className="spec-label">
                    <i className="bi bi-box-seam text-emerald me-2"></i> Stock Status
                  </td>
                  {compareList.map((p) => (
                    <td key={p.id} className="text-center">
                      <span className="badge-pill-glow badge-emerald">
                        <span className="dot-live me-1"></span>
                        {p.availability === 'in_stock' ? 'In Stock' : 'Low Stock'}
                      </span>
                    </td>
                  ))}
                  {Array.from({ length: 3 - compareList.length }).map((_, i) => <td key={i}></td>)}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ComparePage;
