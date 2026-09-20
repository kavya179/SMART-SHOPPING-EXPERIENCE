import React from 'react';
import './StateDisplay.css';

/**
 * Loading spinner state.
 */
export function LoadingState({ message = 'Loading...' }) {
  return (
    <div className="state-display">
      <div className="state-spinner">
        <div className="spinner-ring"></div>
      </div>
      <p className="state-message">{message}</p>
    </div>
  );
}

/**
 * Empty state (no results).
 */
export function EmptyState({ message = 'No products found.', suggestion = 'Try adjusting your filters.' }) {
  return (
    <div className="state-display">
      <div className="state-icon empty">
        <i className="bi bi-search"></i>
      </div>
      <p className="state-message">{message}</p>
      <p className="state-hint">{suggestion}</p>
    </div>
  );
}

/**
 * API error state.
 */
export function ErrorState({ message = 'Something went wrong.', onRetry }) {
  return (
    <div className="state-display">
      <div className="state-icon error">
        <i className="bi bi-exclamation-triangle"></i>
      </div>
      <p className="state-message">{message}</p>
      <p className="state-hint">
        Make sure the Django backend is running at{' '}
        <code>http://localhost:8000</code>
      </p>
      {onRetry && (
        <button className="btn-glow mt-3" onClick={onRetry}>
          <i className="bi bi-arrow-clockwise me-2"></i> Retry
        </button>
      )}
    </div>
  );
}
