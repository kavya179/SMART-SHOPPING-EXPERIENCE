/**
 * API service — single source of truth for all backend calls.
 * Base URL is read from the REACT_APP_API_BASE_URL environment variable.
 */

const API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

/**
 * Generic fetch wrapper with error handling.
 */
async function apiFetch(endpoint, params = {}) {
  const url = new URL(`${API_BASE}${endpoint}`);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.append(key, value);
    }
  });

  const response = await fetch(url.toString());

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `Request failed with status ${response.status}`);
  }

  return response.json();
}

// ── Health ────────────────────────────────────────────────────
export function fetchHealthCheck() {
  return apiFetch('/health/');
}

// ── Products ──────────────────────────────────────────────────
export function fetchProducts(filters = {}) {
  return apiFetch('/products/', filters);
}

export function fetchProductById(id) {
  return apiFetch(`/products/${id}/`);
}

// ── Categories ────────────────────────────────────────────────
export function fetchCategories() {
  return apiFetch('/products/categories/');
}

// ── Personalized Recommendations (Quiz) ──────────────────────
export async function submitQuizRecommendations(quizData) {
  const response = await fetch(`${API_BASE}/recommendations/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(quizData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `Recommendation request failed with status ${response.status}`);
  }

  return response.json();
}

// ── Product FAQ Assistant ─────────────────────────────────────
export async function askFaqAssistant(question, productId = null) {
  const payload = { question };
  if (productId) {
    payload.product_id = productId;
  }

  const response = await fetch(`${API_BASE}/faq/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `FAQ assistant request failed with status ${response.status}`);
  }

  return response.json();
}

export default apiFetch;
