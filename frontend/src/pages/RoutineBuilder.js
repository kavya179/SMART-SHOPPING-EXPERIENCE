import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { buildRoutine } from '../services/api';
import './RoutineBuilder.css';

const SKIN_TYPES = [
  { id: 'oily', label: 'Oily', icon: '💧', desc: 'Prone to shine & enlarged pores' },
  { id: 'dry', label: 'Dry', icon: '🌵', desc: 'Tight, flaky or dehydrated' },
  { id: 'combination', label: 'Combination', icon: '⚖️', desc: 'Oily T-zone, normal cheeks' },
  { id: 'sensitive', label: 'Sensitive', icon: '🌸', desc: 'Easily irritated or reactive' },
  { id: 'all', label: 'Normal', icon: '✨', desc: 'Balanced, no severe concerns' },
];

const CONCERNS = [
  { id: 'acne', label: 'Acne & Pores', icon: '🫧', desc: 'Reduce breakouts & oiliness' },
  { id: 'brightening', label: 'Brightening', icon: '☀️', desc: 'Dark spots & radiance' },
  { id: 'hydration', label: 'Hydration', icon: '💧', desc: '48-hr moisture & plump skin' },
  { id: 'anti-aging', label: 'Anti-Ageing', icon: '⏳', desc: 'Firmness & fine lines' },
  { id: 'redness', label: 'Redness & Calm', icon: '🌿', desc: 'Soothe reactive skin' },
  { id: 'dark spots', label: 'Dark Spots', icon: '🔆', desc: 'Pigmentation & even tone' },
  { id: 'dryness', label: 'Barrier Repair', icon: '🛡️', desc: 'Rich hydration & ceramides' },
  { id: 'general', label: 'General Care', icon: '🧴', desc: 'Balanced everyday routine' },
];

function RoutineStep({ step, timeLabel }) {
  const [expanded, setExpanded] = useState(false);
  const p = step.product;

  return (
    <div className="rb-step animate-in">
      <div className="rb-step-header">
        <div className="rb-step-num">{step.step}</div>
        <div className="rb-step-icon">{step.icon}</div>
        <div className="rb-step-info">
          <span className="rb-step-name">{step.step_name}</span>
          <span className="rb-step-time">{timeLabel}</span>
        </div>
      </div>

      <div className="rb-step-body">
        {p ? (
          <div className="rb-product-found">
            <div className="rb-product-img-wrap">
              {p.image_url ? (
                <img src={p.image_url} alt={p.name} className="rb-product-img" />
              ) : (
                <div className="rb-product-img-placeholder">{step.icon}</div>
              )}
            </div>
            <div className="rb-product-details">
              <Link to={`/products/${p.id}`} className="rb-product-name">
                {p.name}
              </Link>
              <p className="rb-product-brand">{p.brand}</p>
              <div className="rb-product-meta">
                <span className="rb-price">₹{p.discounted_price || p.price}</span>
                {p.discount_percent > 0 && (
                  <span className="rb-price-strike">₹{p.price}</span>
                )}
                {p.rating && (
                  <span className="rb-rating">★ {p.rating}</span>
                )}
              </div>
              {p.key_ingredients && (
                <p className="rb-ingredients">
                  <strong>Key actives:</strong> {p.key_ingredients.split(',').slice(0, 3).join(', ')}
                </p>
              )}
              <div className="rb-step-instruction" onClick={() => setExpanded(!expanded)}>
                <i className={`bi bi-chevron-${expanded ? 'up' : 'down'} me-1`} />
                How to use
              </div>
              {expanded && (
                <p className="rb-instruction-text">{step.instruction}</p>
              )}
            </div>
          </div>
        ) : (
          <div className="rb-no-product">
            <i className="bi bi-search me-2" />
            {step.fallback_tip}
            <Link to="/products" className="rb-browse-link ms-2">Browse →</Link>
          </div>
        )}
      </div>
    </div>
  );
}

function RoutineBuilder() {
  const [skinType, setSkinType] = useState('');
  const [concern, setConcern] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('am');

  const handleBuild = async () => {
    if (!skinType || !concern) {
      setError('Please select your skin type and primary concern to continue.');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await buildRoutine(skinType, concern);
      setResult(data);
      setActiveTab('am');
    } catch (err) {
      setError(err.message || 'Could not build your routine. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSkinType('');
    setConcern('');
    setResult(null);
    setError(null);
  };

  const amSteps = result?.morning_routine?.filter((s) => s.product_found || s.fallback_tip) || [];
  const pmSteps = result?.evening_routine?.filter((s) => s.product_found || s.fallback_tip) || [];

  return (
    <div className="rb-page">
      <div className="container">
        {/* Header */}
        <div className="rb-header glass-card animate-in">
          <div className="rb-header-badge">
            <i className="bi bi-calendar3 me-1" />
            Personalised Skincare Routines
          </div>
          <h1 className="rb-title">
            Beauty <span className="rb-gradient-text">Routine Builder</span>
          </h1>
          <p className="rb-subtitle">
            Tell us your skin type and primary concern. We'll build a complete
            AM & PM skincare routine using real products from our catalog —
            ordered from thinnest to thickest, step by step.
          </p>
        </div>

        {!result ? (
          /* ── Build Form ── */
          <div className="rb-form-panel glass-card animate-in">
            {/* Step 1: Skin Type */}
            <div className="rb-form-section">
              <h3 className="rb-form-heading">
                <span className="rb-step-badge">1</span>
                What is your skin type?
              </h3>
              <div className="rb-options-grid">
                {SKIN_TYPES.map((s) => (
                  <button
                    key={s.id}
                    id={`skin-type-${s.id}`}
                    className={`rb-option-card ${skinType === s.id ? 'selected' : ''}`}
                    onClick={() => setSkinType(s.id)}
                  >
                    <span className="rb-option-icon">{s.icon}</span>
                    <span className="rb-option-label">{s.label}</span>
                    <span className="rb-option-desc">{s.desc}</span>
                    {skinType === s.id && (
                      <span className="rb-check"><i className="bi bi-check-circle-fill" /></span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Step 2: Concern */}
            <div className="rb-form-section">
              <h3 className="rb-form-heading">
                <span className="rb-step-badge">2</span>
                What is your primary skin concern?
              </h3>
              <div className="rb-options-grid concern-grid">
                {CONCERNS.map((c) => (
                  <button
                    key={c.id}
                    id={`concern-${c.id}`}
                    className={`rb-option-card ${concern === c.id ? 'selected' : ''}`}
                    onClick={() => setConcern(c.id)}
                  >
                    <span className="rb-option-icon">{c.icon}</span>
                    <span className="rb-option-label">{c.label}</span>
                    <span className="rb-option-desc">{c.desc}</span>
                    {concern === c.id && (
                      <span className="rb-check"><i className="bi bi-check-circle-fill" /></span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {error && (
              <div className="rb-error-msg">
                <i className="bi bi-exclamation-triangle me-2" />
                {error}
              </div>
            )}

            <div className="rb-form-footer">
              <button
                id="build-routine-btn"
                className="rb-build-btn btn-glow"
                onClick={handleBuild}
                disabled={loading || !skinType || !concern}
              >
                {loading ? (
                  <>
                    <span className="rb-spinner" />
                    Building your routine...
                  </>
                ) : (
                  <>
                    <i className="bi bi-magic me-2" />
                    Build My Routine
                  </>
                )}
              </button>
              <p className="rb-form-note">
                Uses real products from our catalog — results vary based on available inventory.
              </p>
            </div>
          </div>
        ) : (
          /* ── Results ── */
          <div className="rb-results animate-in">
            {/* Result Header */}
            <div className="rb-result-header glass-card">
              <div className="rb-result-badge">
                <i className="bi bi-check-circle-fill me-2" />
                Your Personalised Routine is Ready
              </div>
              <div className="rb-result-meta">
                <span className="rb-result-chip">
                  <i className="bi bi-person me-1" />{result.skin_type_label} Skin
                </span>
                <span className="rb-result-chip">
                  <i className="bi bi-bullseye me-1" />{result.concern_label}
                </span>
                <span className="rb-result-chip">
                  <i className="bi bi-box2 me-1" />{result.total_products_found} Products Matched
                </span>
              </div>
              <button className="btn-glass mt-3" onClick={handleReset}>
                <i className="bi bi-arrow-counterclockwise me-1" />
                Build New Routine
              </button>
            </div>

            {/* AM / PM Tabs */}
            <div className="rb-tabs">
              <button
                className={`rb-tab ${activeTab === 'am' ? 'active' : ''}`}
                onClick={() => setActiveTab('am')}
                id="am-tab-btn"
              >
                ☀️ Morning Routine
                <span className="rb-tab-count">{amSteps.length} steps</span>
              </button>
              <button
                className={`rb-tab ${activeTab === 'pm' ? 'active' : ''}`}
                onClick={() => setActiveTab('pm')}
                id="pm-tab-btn"
              >
                🌙 Evening Routine
                <span className="rb-tab-count">{pmSteps.length} steps</span>
              </button>
            </div>

            {/* Steps */}
            <div className="rb-steps-list">
              {(activeTab === 'am' ? amSteps : pmSteps).map((step) => (
                <RoutineStep
                  key={`${activeTab}-${step.step}`}
                  step={step}
                  timeLabel={activeTab === 'am' ? '☀️ Morning' : '🌙 Evening'}
                />
              ))}
            </div>

            {/* Tips */}
            {result.routine_tips && result.routine_tips.length > 0 && (
              <div className="rb-tips-card glass-card">
                <h4 className="rb-tips-title">
                  <i className="bi bi-lightbulb me-2" />
                  Expert Routine Tips
                </h4>
                <ul className="rb-tips-list">
                  {result.routine_tips.map((tip, idx) => (
                    <li key={idx} className="rb-tip">
                      <i className="bi bi-arrow-right-short me-1 text-primary-light" />
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Disclaimer */}
            <div className="rb-disclaimer">
              <i className="bi bi-info-circle me-2" />
              {result.disclaimer}
            </div>

            {/* CTA */}
            <div className="rb-result-cta">
              <Link to="/ingredient-check" className="btn-glow">
                <i className="bi bi-shield-check me-2" />
                Check Ingredient Safety
              </Link>
              <Link to="/products?category=skincare" className="btn-glass">
                <i className="bi bi-grid me-2" />
                Shop Skincare
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default RoutineBuilder;
