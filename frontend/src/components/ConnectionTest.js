import React, { useState } from 'react';
import './ConnectionTest.css';

const API_BASE = 'http://localhost:8000/api';

function ConnectionTest() {
  const [healthResult, setHealthResult] = useState(null);
  const [productsResult, setProductsResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const testHealth = async () => {
    setLoading(true);
    setError(null);
    setHealthResult(null);
    try {
      const res = await fetch(`${API_BASE}/health/`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setHealthResult(data);
    } catch (err) {
      setError(`Health check failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const testProducts = async () => {
    setLoading(true);
    setError(null);
    setProductsResult(null);
    try {
      const res = await fetch(`${API_BASE}/products/`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setProductsResult(data);
    } catch (err) {
      setError(`Products fetch failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card connection-panel p-4 animate-in animate-delay-4">
      <div className="d-flex align-items-center mb-3">
        <div className="panel-icon">
          <i className="bi bi-plug"></i>
        </div>
        <div className="ms-3">
          <h5 className="mb-0 fw-bold">API Connection Test</h5>
          <small className="text-muted-custom">Verify frontend ↔ backend communication</small>
        </div>
      </div>

      <div className="d-flex gap-2 mb-3 flex-wrap">
        <button
          className="btn-glow"
          onClick={testHealth}
          disabled={loading}
          id="btn-test-health"
        >
          {loading && !productsResult ? (
            <><i className="bi bi-arrow-repeat spin-icon me-2"></i>Testing...</>
          ) : (
            <><i className="bi bi-heart-pulse me-2"></i>Test Health</>
          )}
        </button>
        <button
          className="btn-glow btn-glow-accent"
          onClick={testProducts}
          disabled={loading}
          id="btn-test-products"
        >
          {loading && !healthResult ? (
            <><i className="bi bi-arrow-repeat spin-icon me-2"></i>Loading...</>
          ) : (
            <><i className="bi bi-box-seam me-2"></i>Fetch Products</>
          )}
        </button>
      </div>

      {/* Health check result */}
      {healthResult && (
        <div className="result-box success-box">
          <div className="d-flex align-items-center mb-2">
            <span className="status-badge success">
              <i className="bi bi-check-circle-fill"></i> Connected
            </span>
          </div>
          <pre className="result-json">{JSON.stringify(healthResult, null, 2)}</pre>
        </div>
      )}

      {/* Products result */}
      {productsResult && (
        <div className="result-box success-box">
          <div className="d-flex align-items-center justify-content-between mb-2">
            <span className="status-badge success">
              <i className="bi bi-check-circle-fill"></i> {productsResult.count} Products Loaded
            </span>
          </div>
          <div className="products-preview">
            {productsResult.results && productsResult.results.slice(0, 4).map((p) => (
              <div key={p.id} className="product-preview-card glass-card p-3 mb-2">
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <strong>{p.name}</strong>
                    <div className="text-muted-custom" style={{fontSize: '0.8rem'}}>
                      {p.brand} · {p.category}
                    </div>
                  </div>
                  <div className="text-end">
                    <div className="price-tag">₹{p.price}</div>
                    <div className="rating-tag">
                      <i className="bi bi-star-fill"></i> {p.rating}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {productsResult.count > 4 && (
              <p className="text-muted-custom text-center mt-2" style={{fontSize: '0.8rem'}}>
                + {productsResult.count - 4} more products
              </p>
            )}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="result-box error-box">
          <span className="status-badge error">
            <i className="bi bi-exclamation-triangle-fill"></i> Error
          </span>
          <p className="mt-2 mb-0">{error}</p>
          <small className="text-muted-custom">
            Make sure Django is running on <code>http://localhost:8000</code>
          </small>
        </div>
      )}
    </div>
  );
}

export default ConnectionTest;
