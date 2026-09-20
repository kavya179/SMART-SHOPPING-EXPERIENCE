import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { checkIngredients } from '../services/api';
import './IngredientChecker.css';

const QUICK_COMBOS = [
  { label: 'Vitamin C + Retinol', ingredients: ['Vitamin C', 'Retinol'] },
  { label: 'Niacinamide + Salicylic Acid', ingredients: ['Niacinamide', 'Salicylic Acid'] },
  { label: 'AHA + BHA + Retinol', ingredients: ['Glycolic Acid', 'Salicylic Acid', 'Retinol'] },
  { label: 'Vitamin C + Niacinamide + SPF', ingredients: ['Vitamin C', 'Niacinamide', 'SPF'] },
  { label: 'Ceramides + Hyaluronic Acid', ingredients: ['Ceramides', 'Hyaluronic Acid'] },
  { label: 'Retinol + Benzoyl Peroxide', ingredients: ['Retinol', 'Benzoyl Peroxide'] },
];

const POPULAR_INGREDIENTS = [
  'Vitamin C', 'Retinol', 'Niacinamide', 'Hyaluronic Acid',
  'Salicylic Acid', 'Glycolic Acid', 'Lactic Acid', 'Benzoyl Peroxide',
  'Ceramides', 'Peptides', 'SPF', 'Kojic Acid', 'Copper Peptide', 'Tretinoin',
];

function IngredientChecker() {
  const [inputText, setInputText] = useState('');
  const [tagList, setTagList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const addIngredient = (name) => {
    const clean = name.trim();
    if (!clean) return;
    if (tagList.find((t) => t.toLowerCase() === clean.toLowerCase())) return;
    if (tagList.length >= 10) return;
    setTagList((prev) => [...prev, clean]);
    setInputText('');
  };

  const handleInputKeyDown = (e) => {
    if ((e.key === 'Enter' || e.key === ',') && inputText.trim()) {
      e.preventDefault();
      addIngredient(inputText);
    }
    if (e.key === 'Backspace' && !inputText && tagList.length > 0) {
      setTagList((prev) => prev.slice(0, -1));
    }
  };

  const removeTag = (idx) => {
    setTagList((prev) => prev.filter((_, i) => i !== idx));
    setResult(null);
  };

  const loadCombo = (combo) => {
    setTagList(combo.ingredients);
    setResult(null);
    setError(null);
  };

  const handleCheck = async () => {
    if (tagList.length < 1) {
      setError('Add at least one ingredient to check.');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await checkIngredients(tagList);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setTagList([]);
    setInputText('');
    setResult(null);
    setError(null);
  };

  const safetyClass = result
    ? result.overall_safety === 'safe'
      ? 'safe'
      : result.overall_safety === 'unsafe'
      ? 'unsafe'
      : result.overall_safety === 'caution'
      ? 'caution'
      : 'low-risk'
    : '';

  return (
    <div className="ic-page">
      <div className="container">
        {/* Header */}
        <div className="ic-header glass-card animate-in">
          <div className="ic-header-badge">
            <i className="bi bi-shield-check me-1" />
            AI-Powered Safety Analysis
          </div>
          <h1 className="ic-title">
            Ingredient <span className="ic-gradient-text">Safety Checker</span>
          </h1>
          <p className="ic-subtitle">
            Enter the active ingredients from your skincare products to instantly detect
            known interaction conflicts, irritation risks, and optimal pairing strategies.
          </p>
          <div className="ic-meta-tags">
            <span className="ic-meta-chip"><i className="bi bi-database me-1" />Curated conflict database</span>
            <span className="ic-meta-chip"><i className="bi bi-lightning me-1" />Instant analysis</span>
            <span className="ic-meta-chip"><i className="bi bi-person-heart me-1" />Educational use only</span>
          </div>
        </div>

        <div className="ic-main-grid">
          {/* Left Panel — Input */}
          <div className="ic-input-panel glass-card animate-in">
            <h3 className="ic-panel-title">
              <i className="bi bi-capsule-pill me-2" />
              Enter Ingredients
            </h3>
            <p className="ic-panel-sub">Type an ingredient and press Enter or comma to add it. Add up to 10 ingredients.</p>

            {/* Tag Input */}
            <div className={`ic-tag-input-wrap ${tagList.length > 0 ? 'has-tags' : ''}`}>
              {tagList.map((tag, idx) => (
                <span key={idx} className="ic-tag">
                  {tag}
                  <button className="ic-tag-remove" onClick={() => removeTag(idx)} aria-label={`Remove ${tag}`}>
                    <i className="bi bi-x" />
                  </button>
                </span>
              ))}
              {tagList.length < 10 && (
                <input
                  id="ingredient-input"
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={handleInputKeyDown}
                  placeholder={tagList.length === 0 ? 'e.g. Vitamin C, Retinol...' : 'Add more...'}
                  className="ic-tag-field"
                  autoComplete="off"
                />
              )}
            </div>

            {/* Popular Ingredient Chips */}
            <div className="ic-popular-section">
              <span className="ic-popular-label">Quick add:</span>
              <div className="ic-popular-chips">
                {POPULAR_INGREDIENTS.map((ing) => (
                  <button
                    key={ing}
                    className={`ic-popular-chip ${tagList.find((t) => t.toLowerCase() === ing.toLowerCase()) ? 'selected' : ''}`}
                    onClick={() => addIngredient(ing)}
                    disabled={tagList.length >= 10}
                  >
                    {ing}
                  </button>
                ))}
              </div>
            </div>

            {/* Action buttons */}
            <div className="ic-actions">
              <button
                id="check-ingredients-btn"
                className="ic-check-btn btn-glow"
                onClick={handleCheck}
                disabled={loading || tagList.length === 0}
              >
                {loading ? (
                  <>
                    <span className="ic-spinner" />
                    Analysing...
                  </>
                ) : (
                  <>
                    <i className="bi bi-shield-check me-2" />
                    Check Safety
                  </>
                )}
              </button>
              {tagList.length > 0 && (
                <button className="btn-glass" onClick={handleClear}>
                  <i className="bi bi-arrow-counterclockwise me-1" />
                  Clear
                </button>
              )}
            </div>

            {error && (
              <div className="ic-error-msg">
                <i className="bi bi-exclamation-triangle me-2" />
                {error}
              </div>
            )}

            {/* Quick Combos */}
            <div className="ic-combos-section">
              <h5 className="ic-combos-title">
                <i className="bi bi-lightning me-1" />
                Popular Combinations to Test
              </h5>
              <div className="ic-combos-grid">
                {QUICK_COMBOS.map((combo, idx) => (
                  <button key={idx} className="ic-combo-card" onClick={() => loadCombo(combo)}>
                    <span className="ic-combo-label">{combo.label}</span>
                    <div className="ic-combo-tags">
                      {combo.ingredients.map((ing, i) => (
                        <span key={i} className="ic-combo-tag">{ing}</span>
                      ))}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right Panel — Results */}
          <div className="ic-result-panel">
            {!result && !loading && (
              <div className="ic-empty-state glass-card animate-in">
                <div className="ic-empty-icon">🧪</div>
                <h4>Your Safety Report Will Appear Here</h4>
                <p>Add ingredients from the left panel and click "Check Safety" to see a detailed conflict analysis.</p>
              </div>
            )}

            {loading && (
              <div className="ic-loading-state glass-card animate-in">
                <div className="ic-loading-icon">⚗️</div>
                <h4>Analysing {tagList.length} Ingredient{tagList.length !== 1 ? 's' : ''}...</h4>
                <p>Cross-referencing our cosmetic chemistry conflict database...</p>
                <div className="ic-progress-bar"><div className="ic-progress-fill" /></div>
              </div>
            )}

            {result && (
              <div className="ic-results animate-in">
                {/* Overall Safety Banner */}
                <div className={`ic-safety-banner glass-card ${safetyClass}`}>
                  <div className="ic-safety-icon">
                    {result.overall_safety === 'safe' ? '✅' :
                     result.overall_safety === 'unsafe' ? '⛔' :
                     result.overall_safety === 'caution' ? '⚠️' : '💡'}
                  </div>
                  <div>
                    <div className="ic-safety-label">{result.overall_label}</div>
                    <div className="ic-safety-meta">
                      {result.total_ingredients_checked} ingredient{result.total_ingredients_checked !== 1 ? 's' : ''} analysed
                      {result.total_conflicts > 0
                        ? ` • ${result.total_conflicts} conflict${result.total_conflicts !== 1 ? 's' : ''} found`
                        : ' • No conflicts found'}
                    </div>
                  </div>
                </div>

                {/* Conflict Cards */}
                {result.conflicts && result.conflicts.length > 0 && (
                  <div className="ic-conflicts-section">
                    <h4 className="ic-section-title">
                      <i className="bi bi-exclamation-triangle me-2" />
                      Detected Conflicts
                    </h4>
                    {result.conflicts.map((conflict, idx) => (
                      <div key={idx} className={`ic-conflict-card glass-card severity-${conflict.severity}`}>
                        <div className="ic-conflict-header">
                          <div className="ic-conflict-pair">
                            <span className="ic-ing-badge">{conflict.ingredient_a}</span>
                            <i className="bi bi-plus-slash-minus mx-2 text-muted" />
                            <span className="ic-ing-badge">{conflict.ingredient_b}</span>
                          </div>
                          <span className={`ic-severity-badge sev-${conflict.severity}`}>
                            {conflict.severity_label}
                          </span>
                        </div>
                        <p className="ic-conflict-reason">{conflict.reason}</p>
                        <div className="ic-conflict-rec">
                          <i className="bi bi-lightbulb me-2" />
                          {conflict.recommendation}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Safe Pairs */}
                {result.safe_pairs && result.safe_pairs.length > 0 && (
                  <div className="ic-safe-section glass-card">
                    <h5 className="ic-section-title safe-title">
                      <i className="bi bi-check-circle me-2" />
                      Safe Combinations
                    </h5>
                    <div className="ic-safe-pairs">
                      {result.safe_pairs.map((pair, idx) => (
                        <div key={idx} className="ic-safe-pair">
                          <i className="bi bi-check2 me-1 text-success" />
                          <strong>{pair.ingredient_a}</strong>
                          <span className="mx-1 text-muted">+</span>
                          <strong>{pair.ingredient_b}</strong>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Disclaimer */}
                <div className="ic-disclaimer">
                  <i className="bi bi-info-circle me-2" />
                  {result.disclaimer}
                </div>

                {/* CTA */}
                <div className="ic-result-cta">
                  <Link to="/routine" className="btn-glow">
                    <i className="bi bi-calendar3 me-2" />
                    Build My Safe Routine
                  </Link>
                  <Link to="/products" className="btn-glass">
                    <i className="bi bi-grid me-2" />
                    Shop Products
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default IngredientChecker;
