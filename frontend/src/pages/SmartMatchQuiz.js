import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { submitQuizRecommendations } from '../services/api';
import './SmartMatchQuiz.css';

// ── Step 1: Categories ──────────────────────────────────────────
const CATEGORIES = [
  { id: 'skincare', name: 'Skincare', icon: 'bi-droplet-half', desc: 'Serums, moisturizers & soothing gels' },
  { id: 'haircare', name: 'Haircare', icon: 'bi-scissors', desc: 'Smoothing shampoos, conditioners & oils' },
  { id: 'makeup', name: 'Makeup', icon: 'bi-brush', desc: 'Matte lipsticks & SPF liquid foundations' },
  { id: 'fragrance', name: 'Fragrance', icon: 'bi-flower1', desc: 'Floral, oriental & luxury parfums' },
  { id: 'bodycare', name: 'Body Care', icon: 'bi-heart-pulse', desc: 'Nourishing lotions & exfoliating scrubs' },
  { id: 'nailcare', name: 'Nail Care', icon: 'bi-palette', desc: 'Gel-effect chip-resistant polishes' },
];

// ── Step 2: Category-Adaptive Profiles ──────────────────────────
const PROFILE_OPTIONS = {
  skincare: {
    title: 'What is your primary skin type?',
    subtitle: 'We match active concentrations to your skin barrier.',
    options: [
      { id: 'dry', label: 'Dry Skin', desc: 'Feels tight, flaky, or dehydrated', icon: 'bi-cloud-drizzle' },
      { id: 'oily', label: 'Oily Skin', desc: 'Prone to shine, enlarged pores & blemishes', icon: 'bi-shield-shaded' },
      { id: 'combination', label: 'Combination', desc: 'Oily T-zone with normal/dry cheeks', icon: 'bi-pie-chart' },
      { id: 'sensitive', label: 'Sensitive Skin', desc: 'Easily irritated, prone to redness', icon: 'bi-shield-exclamation' },
      { id: 'all', label: 'Normal / Balanced', desc: 'Generally balanced, no severe dryness or oil', icon: 'bi-check-circle' },
    ],
  },
  haircare: {
    title: 'What is your hair profile & texture?',
    subtitle: 'Select your main hair condition to tailor smoothing & strengthening actives.',
    options: [
      { id: 'frizz', label: 'Frizzy & Dry', desc: 'Needs deep keratin smoothing and moisture', icon: 'bi-wind' },
      { id: 'hairfall', label: 'Thinning / Breakage', desc: 'Needs strengthening biotin and caffeine', icon: 'bi-arrow-down-right-circle' },
      { id: 'all', label: 'Normal / Daily Care', desc: 'Seeking healthy shine, softness & volume', icon: 'bi-sparkles' },
    ],
  },
  makeup: {
    title: 'What is your desired finish & coverage?',
    subtitle: 'Choose how you want your cosmetic products to look and feel.',
    options: [
      { id: 'matte finish', label: 'Velvet Matte', desc: 'Long-lasting, non-drying bold color', icon: 'bi-square-fill' },
      { id: 'coverage', label: 'Natural Base with SPF', desc: 'Seamless medium coverage with sun defense', icon: 'bi-sun' },
      { id: 'all', label: 'Versatile Daily Wear', desc: 'Comfortable wear for day to night', icon: 'bi-stars' },
    ],
  },
  fragrance: {
    title: 'What scent notes do you gravitate towards?',
    subtitle: 'Find a scent that reflects your personal presence.',
    options: [
      { id: 'evening wear', label: 'Warm Floral & Oriental', desc: 'Jasmine, vanilla bean & sandalwood', icon: 'bi-moon-stars' },
      { id: 'all', label: 'All Scent Families', desc: 'Open to discovering new signature scents', icon: 'bi-flower2' },
    ],
  },
  bodycare: {
    title: 'What is your primary body care focus?',
    subtitle: 'Tailor hydration or deep cleansing for your body.',
    options: [
      { id: 'dryness', label: 'All-Day Nourishment', desc: 'Cocoa butter and deep barrier hydration', icon: 'bi-droplet' },
      { id: 'exfoliation', label: 'Detox & Exfoliation', desc: 'Charcoal scrub to remove impurities & dead skin', icon: 'bi-gem' },
    ],
  },
  nailcare: {
    title: 'What do you look for in nail formulas?',
    subtitle: 'Select your preferred finish and performance.',
    options: [
      { id: 'glossy', label: 'High-Shine Gel Finish', desc: 'Chip-resistant formula without UV lamp', icon: 'bi-palette' },
      { id: 'all', label: 'Nail Health & Strength', desc: 'Infused with biotin and keratin', icon: 'bi-shield-check' },
    ],
  },
};

// ── Step 3: Category-Adaptive Concerns / Goals ──────────────────
const CONCERN_OPTIONS = {
  skincare: [
    { id: 'brightening', label: '✨ Dark Spots & Dullness', desc: 'Boost radiance and even out skin tone' },
    { id: 'hydration', label: '💧 Deep Hydration & Barrier', desc: 'Lock in 48-hr moisture without greasiness' },
    { id: 'acne', label: '🌿 Acne, Oil & Large Pores', desc: 'Minimize sebum and clarify texture' },
    { id: 'redness', label: '🌸 Redness, Irritation & Sunburn', desc: 'Calm and soothe reactive skin' },
  ],
  haircare: [
    { id: 'frizz', label: '💆‍♀️ Frizz Control & Smoothing', desc: 'Tame wild flyaways with keratin & argan oil' },
    { id: 'hairfall', label: '💪 Hairfall & Breakage Reduction', desc: 'Fortify roots with biotin and caffeine' },
    { id: 'damage', label: '✨ Split Ends & Deep Moisture', desc: 'Restore damaged lengths and add shine' },
  ],
  makeup: [
    { id: 'long-lasting', label: '💄 Hydrating Matte Lip Color', desc: 'Velvety finish with jojoba hydration' },
    { id: 'coverage', label: '☀️ Flawless Skin Tint with SPF', desc: 'Even tone with daily SPF 25 filter' },
  ],
  fragrance: [
    { id: 'long-lasting', label: '🌙 Long-Lasting Evening Scent', desc: 'Enchanting floral-oriental sillage' },
    { id: 'floral', label: '🌸 Fresh & Romantic Floral', desc: 'Jasmine and vanilla harmony' },
  ],
  bodycare: [
    { id: 'dryness', label: '🥥 24-Hr Moisture & Softness', desc: 'Cocoa butter and coconut oil nourishment' },
    { id: 'exfoliation', label: '🧼 Deep Pore Scrub & Smoothing', desc: 'Activated charcoal and walnut exfoliation' },
  ],
  nailcare: [
    { id: 'chip-resistant', label: '💅 Chip-Resistant Gel Shine', desc: 'Long-wear salon gel effect' },
  ],
};

// ── Step 4: Budget Ranges ───────────────────────────────────────
const BUDGET_OPTIONS = [
  { id: '400', label: 'Under ₹400', desc: 'Budget-friendly essentials' },
  { id: '650', label: 'Under ₹650', desc: 'Popular mid-range favorites' },
  { id: '1000', label: 'Under ₹1,000', desc: 'Premium treatment formulas' },
  { id: '', label: 'Any Budget', desc: 'Show all matching prices' },
];

// ── Step 5: Preferred Actives ───────────────────────────────────
const INGREDIENT_CHIPS = {
  skincare: ['Vitamin C', 'Niacinamide', 'Hyaluronic Acid', 'Ceramides', 'Aloe Vera', 'Squalane'],
  haircare: ['Keratin', 'Argan Oil', 'Biotin', 'Caffeine', 'Coconut Oil'],
  makeup: ['Jojoba Oil', 'Niacinamide', 'Hyaluronic Acid', 'SPF Filters'],
  fragrance: ['Jasmine', 'Vanilla', 'Sandalwood', 'Musk'],
  bodycare: ['Cocoa Butter', 'Charcoal', 'Shea Butter', 'Tea Tree Oil'],
  nailcare: ['Biotin', 'Calcium', 'Keratin'],
};

function SmartMatchQuiz() {
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 5;

  // Answers State
  const [category, setCategory] = useState('skincare');
  const [skinType, setSkinType] = useState('dry');
  const [concern, setConcern] = useState('hydration');
  const [budgetMax, setBudgetMax] = useState('650');
  const [selectedIngredients, setSelectedIngredients] = useState([]);

  // Result State
  const [loading, setLoading] = useState(false);
  const [resultsData, setResultsData] = useState(null);
  const [error, setError] = useState(null);

  // When category changes, reset sub-fields to sensible defaults
  const handleCategorySelect = (catId) => {
    setCategory(catId);
    const profs = PROFILE_OPTIONS[catId]?.options || [];
    if (profs.length > 0) setSkinType(profs[0].id);

    const concerns = CONCERN_OPTIONS[catId] || [];
    if (concerns.length > 0) setConcern(concerns[0].id);

    setSelectedIngredients([]);
  };

  const handleIngredientToggle = (ing) => {
    setSelectedIngredients((prev) =>
      prev.includes(ing) ? prev.filter((i) => i !== ing) : [...prev, ing]
    );
  };

  const handleSubmitQuiz = async () => {
    setLoading(true);
    setError(null);

    const payload = {
      category,
      skin_type: skinType,
      concern,
      budget_max: budgetMax ? Number(budgetMax) : null,
      preferred_ingredients: selectedIngredients,
    };

    try {
      const data = await submitQuizRecommendations(payload);
      setResultsData(data);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setError(err.message || 'Failed to generate recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRetake = () => {
    setResultsData(null);
    setCurrentStep(1);
    setCategory('skincare');
    setSkinType('dry');
    setConcern('hydration');
    setBudgetMax('650');
    setSelectedIngredients([]);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleEditAnswers = () => {
    setResultsData(null);
    setCurrentStep(1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // ─────────────────────────────────────────────────────────────
  // RENDER: Results View
  // ─────────────────────────────────────────────────────────────
  if (resultsData) {
    const { recommendations, is_alternative, message, query_summary } = resultsData;

    return (
      <div className="quiz-page-wrapper">
        <div className="container">
          {/* Results Hero Header */}
          <div className="results-hero-card glass-card p-4 p-md-5 mb-5 text-center">
            <div className="results-icon-badge mb-3">
              <i className="bi bi-stars"></i>
            </div>
            <span className="badge-pill-glow badge-violet mb-2">
              <i className="bi bi-cpu me-1"></i> Rule-Based Formulation Matching
            </span>
            <h1 className="results-main-title">
              Your Personalized <span className="gradient-text">SmartMatch Routine</span>
            </h1>
            <p className="results-main-sub mx-auto mb-4">{message}</p>

            {/* Answer Profile Chips */}
            <div className="d-flex flex-wrap justify-content-center gap-2 mb-4">
              <span className="profile-summary-chip">
                <i className="bi bi-grid me-1"></i> Category: <strong>{query_summary.category}</strong>
              </span>
              {query_summary.skin_type && query_summary.skin_type !== 'all' && (
                <span className="profile-summary-chip">
                  <i className="bi bi-droplet me-1"></i> Profile: <strong>{query_summary.skin_type}</strong>
                </span>
              )}
              {query_summary.concern && (
                <span className="profile-summary-chip">
                  <i className="bi bi-target me-1"></i> Concern: <strong>{query_summary.concern}</strong>
                </span>
              )}
              {query_summary.budget_max && (
                <span className="profile-summary-chip">
                  <i className="bi bi-cash me-1"></i> Budget: <strong>Under ₹{query_summary.budget_max}</strong>
                </span>
              )}
            </div>

            {/* Actions Bar */}
            <div className="d-flex flex-wrap justify-content-center gap-3">
              <button className="btn-glass" onClick={handleEditAnswers}>
                <i className="bi bi-pencil-square me-2"></i> Edit Answers
              </button>
              <button className="btn-glass" onClick={handleRetake}>
                <i className="bi bi-arrow-counterclockwise me-2"></i> Restart Finder
              </button>
              <Link to="/products" className="btn-glow">
                <i className="bi bi-grid-3x3-gap me-2"></i> View Full Catalog
              </Link>
            </div>
          </div>

          {/* Alternative Disclaimer if needed */}
          {is_alternative && (
            <div className="alternative-alert-banner glass-card p-4 mb-4">
              <div className="d-flex align-items-center gap-3">
                <i className="bi bi-info-circle-fill text-warning fs-3"></i>
                <div>
                  <h6 className="fw-bold text-warning mb-1">Closest Available Formulations</h6>
                  <p className="mb-0 text-muted fs-85">
                    No products strictly matched every constraint. Below are the closest, top-rated alternatives matching your formulation needs.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Recommended Product Cards with Explanation */}
          <div className="row g-4 mb-5">
            {recommendations.map((item, idx) => {
              const { product, match_percentage, reasons } = item;
              return (
                <div className="col-lg-6" key={product.id || idx}>
                  <div className="matched-product-card glass-card p-4 h-100 d-flex flex-column justify-content-between">
                    <div>
                      {/* Top Match Badge */}
                      <div className="d-flex align-items-center justify-content-between mb-3">
                        <span className="match-score-pill">
                          <i className="bi bi-award-fill text-warning me-1"></i>
                          {match_percentage}% Formulation Match
                        </span>
                        <span className="badge-pill-glow badge-violet">
                          #{idx + 1} Best Match
                        </span>
                      </div>

                      {/* Product Preview Row */}
                      <div className="d-flex gap-3 align-items-center mb-3">
                        <img
                          src={product.image_url}
                          alt={product.name}
                          className="matched-prod-thumbnail"
                        />
                        <div>
                          <span className="matched-prod-cat text-primary-light">{product.category}</span>
                          <h4 className="matched-prod-title mb-1">
                            <Link to={`/products/${product.id}`} className="text-white text-decoration-none">
                              {product.name}
                            </Link>
                          </h4>
                          <span className="matched-prod-brand">{product.brand}</span>
                          <div className="matched-prod-price mt-1">
                            <span className="price-bold">₹{product.discounted_price || product.price}</span>
                            {product.discount_percent > 0 && (
                              <span className="price-strike ms-2">₹{product.price}</span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Why This Matches Rationale Box */}
                      <div className="why-matches-box p-3 mb-3">
                        <div className="why-matches-title mb-2">
                          <i className="bi bi-magic text-primary-light me-1"></i>
                          <span>Why this matches your profile:</span>
                        </div>
                        <ul className="why-matches-list mb-0">
                          {reasons.map((reason, rIdx) => (
                            <li key={rIdx}>
                              <i className="bi bi-check2 text-success me-2"></i>
                              {reason}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Card Actions */}
                    <div className="d-flex gap-2 mt-auto pt-2">
                      <Link to={`/products/${product.id}`} className="btn-glow flex-grow-1">
                        View Product Details <i className="bi bi-arrow-right ms-1"></i>
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  // ─────────────────────────────────────────────────────────────
  // RENDER: Multi-Step Quiz Wizard
  // ─────────────────────────────────────────────────────────────
  const profileConfig = PROFILE_OPTIONS[category] || PROFILE_OPTIONS.skincare;
  const concernsList = CONCERN_OPTIONS[category] || CONCERN_OPTIONS.skincare;
  const ingredientChoices = INGREDIENT_CHIPS[category] || INGREDIENT_CHIPS.skincare;

  return (
    <div className="quiz-page-wrapper">
      <div className="container">
        {/* Quiz Progress & Header */}
        <div className="quiz-header text-center mb-5">
          <span className="badge-pill-glow badge-violet mb-2">
            <i className="bi bi-magic me-1"></i> Guided Beauty Discovery
          </span>
          <h1 className="quiz-title">
            Personalized <span className="gradient-text">Product Finder</span>
          </h1>
          <p className="quiz-subtitle">
            Answer 5 quick questions and our rule-based formulation engine will find your ideal match.
          </p>

          {/* Progress Indicator */}
          <div className="quiz-progress-container mt-4 mx-auto">
            <div className="quiz-progress-labels d-flex justify-content-between align-items-center mb-2">
              <span className="quiz-progress-step-text">Step {currentStep} of {totalSteps}</span>
              <span className="quiz-progress-pct-text">{Math.round((currentStep / totalSteps) * 100)}% Completed</span>
            </div>
            <div className="progress-track">
              <div
                className="progress-fill"
                style={{ width: `${(currentStep / totalSteps) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Multi-Step Question Card */}
        <div className="quiz-step-card glass-card p-4 p-md-5 mx-auto">
          {loading ? (
            <div className="quiz-loading-state text-center py-5">
              <div className="spinner-border text-primary-light mb-3" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
              <h4 className="fw-bold mb-2">Analyzing Product Formulations...</h4>
              <p className="text-muted">Our rule-based engine is evaluating your skin profile and matching active ingredients.</p>
            </div>
          ) : error ? (
            <div className="quiz-error-state text-center py-5">
              <i className="bi bi-exclamation-triangle-fill text-danger fs-1 mb-3 d-block"></i>
              <h4 className="fw-bold mb-2">Matching Error</h4>
              <p className="text-muted mb-4">{error}</p>
              <button className="btn-glow" onClick={handleSubmitQuiz}>
                <i className="bi bi-arrow-clockwise me-1"></i> Try Again
              </button>
            </div>
          ) : (
            <>
              {/* ── STEP 1: Category Selection ────────────────────── */}
              {currentStep === 1 && (
                <div className="step-content animate-in">
                  <h3 className="step-question-title">What personal-care category are you shopping for?</h3>
                  <p className="step-question-desc">Select the main category you want to build your routine or find a match for.</p>

                  <div className="row g-3">
                    {CATEGORIES.map((cat) => (
                      <div className="col-md-6 col-lg-4" key={cat.id}>
                        <div
                          className={`quiz-option-card ${category === cat.id ? 'active' : ''}`}
                          onClick={() => handleCategorySelect(cat.id)}
                        >
                          <div className="option-icon-box">
                            <i className={`bi ${cat.icon}`}></i>
                          </div>
                          <h5 className="option-name">{cat.name}</h5>
                          <span className="option-desc">{cat.desc}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── STEP 2: Skin Profile / Intended Use ───────────── */}
              {currentStep === 2 && (
                <div className="step-content animate-in">
                  <h3 className="step-question-title">{profileConfig.title}</h3>
                  <p className="step-question-desc">{profileConfig.subtitle}</p>

                  <div className="row g-3">
                    {profileConfig.options.map((item) => (
                      <div className="col-md-6 col-lg-4" key={item.id}>
                        <div
                          className={`quiz-option-card ${skinType === item.id ? 'active' : ''}`}
                          onClick={() => setSkinType(item.id)}
                        >
                          <div className="option-icon-box">
                            <i className={`bi ${item.icon}`}></i>
                          </div>
                          <h5 className="option-name">{item.label}</h5>
                          <span className="option-desc">{item.desc}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── STEP 3: Primary Concern ──────────────────────── */}
              {currentStep === 3 && (
                <div className="step-content animate-in">
                  <h3 className="step-question-title">What is your primary goal or concern?</h3>
                  <p className="step-question-desc">We will match active ingredients specifically proven to target this concern.</p>

                  <div className="row g-3">
                    {concernsList.map((c) => (
                      <div className="col-md-6" key={c.id}>
                        <div
                          className={`quiz-option-card ${concern === c.id ? 'active' : ''}`}
                          onClick={() => setConcern(c.id)}
                        >
                          <h5 className="option-name mb-1">{c.label}</h5>
                          <span className="option-desc">{c.desc}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── STEP 4: Budget Range ─────────────────────────── */}
              {currentStep === 4 && (
                <div className="step-content animate-in">
                  <h3 className="step-question-title">What is your target budget for this product?</h3>
                  <p className="step-question-desc">We will filter out products beyond your budget or rank best-value options first.</p>

                  <div className="row g-3 mb-4">
                    {BUDGET_OPTIONS.map((b) => (
                      <div className="col-md-6" key={b.id || 'any'}>
                        <div
                          className={`quiz-option-card ${budgetMax === b.id ? 'active' : ''}`}
                          onClick={() => setBudgetMax(b.id)}
                        >
                          <h5 className="option-name mb-1">{b.label}</h5>
                          <span className="option-desc">{b.desc}</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="custom-budget-input p-3 glass-card">
                    <label className="fs-8 text-muted d-block mb-2">Or enter an exact maximum price (₹):</label>
                    <input
                      type="number"
                      placeholder="e.g. 750"
                      value={budgetMax}
                      onChange={(e) => setBudgetMax(e.target.value)}
                      className="quiz-text-input"
                    />
                  </div>
                </div>
              )}

              {/* ── STEP 5: Ingredients & Preferences ────────────── */}
              {currentStep === 5 && (
                <div className="step-content animate-in">
                  <h3 className="step-question-title">Any preferred active ingredients? (Optional)</h3>
                  <p className="step-question-desc">Select any specific actives you love to boost matching priority.</p>

                  <div className="quiz-ingredients-grid d-flex flex-wrap gap-3 mb-4">
                    {ingredientChoices.map((ing) => {
                      const isSelected = selectedIngredients.includes(ing.toLowerCase());
                      return (
                        <button
                          key={ing}
                          type="button"
                          className={`ingredient-chip-btn ${isSelected ? 'active' : ''}`}
                          onClick={() => handleIngredientToggle(ing.toLowerCase())}
                        >
                          <i className={`bi ${isSelected ? 'bi-check-circle-fill' : 'bi-plus-circle'} me-2`}></i>
                          <span>{ing}</span>
                        </button>
                      );
                    })}
                  </div>

                  {/* Summary preview before submit */}
                  <div className="quiz-summary-box p-4 glass-card mt-4">
                    <div className="quiz-summary-header mb-3">
                      <i className="bi bi-card-checklist me-2 text-rose"></i>
                      <strong>Your Selected Match Criteria:</strong>
                    </div>
                    <div className="quiz-summary-tags-grid">
                      <div className="quiz-summary-tag-item">
                        <span className="summary-tag-label">Category</span>
                        <span className="summary-tag-value">{category}</span>
                      </div>
                      <div className="quiz-summary-tag-item">
                        <span className="summary-tag-label">Skin Profile</span>
                        <span className="summary-tag-value">{skinType}</span>
                      </div>
                      <div className="quiz-summary-tag-item">
                        <span className="summary-tag-label">Primary Goal</span>
                        <span className="summary-tag-value">{concern}</span>
                      </div>
                      <div className="quiz-summary-tag-item">
                        <span className="summary-tag-label">Max Budget</span>
                        <span className="summary-tag-value">{budgetMax ? `Under ₹${budgetMax}` : 'Any Budget'}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* ── Navigation Buttons ────────────────────────────── */}
              <div className="quiz-nav-row d-flex justify-content-between align-items-center mt-5 pt-4 border-top border-secondary-subtle">
                <button
                  type="button"
                  className="btn-glass"
                  onClick={() => setCurrentStep((prev) => Math.max(1, prev - 1))}
                  disabled={currentStep === 1}
                >
                  <i className="bi bi-arrow-left me-2"></i> Back
                </button>

                {currentStep < totalSteps ? (
                  <button
                    type="button"
                    className="btn-glow"
                    onClick={() => setCurrentStep((prev) => Math.min(totalSteps, prev + 1))}
                  >
                    Next Step <i className="bi bi-arrow-right ms-2"></i>
                  </button>
                ) : (
                  <button
                    type="button"
                    className="btn-glow btn-rose"
                    onClick={handleSubmitQuiz}
                  >
                    <i className="bi bi-magic me-2"></i> Find My Matches
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default SmartMatchQuiz;
