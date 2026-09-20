import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

function Footer() {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);

  const handleSubscribe = (e) => {
    e.preventDefault();
    if (email.trim()) {
      setSubscribed(true);
      setEmail('');
    }
  };

  return (
    <footer className="luxury-footer">
      <div className="container">
        {/* Top Newsletter & Brand Bar */}
        <div className="footer-top-card glass-card p-4 p-md-5 mb-5">
          <div className="row align-items-center gy-4">
            <div className="col-lg-6">
              <span className="badge-pill-glow badge-violet mb-2">
                <i className="bi bi-envelope-heart me-1"></i> The Beauty Insider
              </span>
              <h3 className="footer-newsletter-title">Get Smart Formulation Drops</h3>
              <p className="footer-newsletter-sub mb-0">
                Receive weekly ingredient breakdowns, newly matched products, and exclusive hackathon updates.
              </p>
            </div>
            <div className="col-lg-6">
              {subscribed ? (
                <div className="subscribed-success-box p-3 text-center">
                  <i className="bi bi-check2-circle text-success fs-4 me-2"></i>
                  <span className="fw-bold">You're on the list! Welcome to SmartMatch.</span>
                </div>
              ) : (
                <form onSubmit={handleSubscribe} className="footer-subscribe-form">
                  <input
                    type="email"
                    placeholder="Enter your email address..."
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="footer-email-input"
                  />
                  <button type="submit" className="btn-glow footer-sub-btn">
                    Subscribe <i className="bi bi-arrow-right"></i>
                  </button>
                </form>
              )}
            </div>
          </div>
        </div>

        {/* Navigation Grid */}
        <div className="row gy-4 mb-5">
          <div className="col-lg-4 col-md-6">
            <div className="footer-brand-wrap mb-3">
              <div className="brand-logo-glow me-2">
                <i className="bi bi-stars"></i>
              </div>
              <span className="footer-brand-title">
                <span className="gradient-text">Joyory</span> SmartMatch
              </span>
            </div>
            <p className="footer-brand-desc mb-3">
              An intelligent, full-stack shopping and recommendation experience for beauty and personal care. Formulated with transparency, powered by science.
            </p>
            <div className="footer-trust-chips d-flex flex-wrap gap-2">
              <span className="trust-badge-pill"><i className="bi bi-shield-check text-success"></i> 100% Authentic</span>
              <span className="trust-badge-pill"><i className="bi bi-droplet text-primary-light"></i> Clean INCI</span>
              <span className="trust-badge-pill"><i className="bi bi-heart-fill text-danger"></i> Cruelty-Free</span>
            </div>
          </div>

          <div className="col-lg-2 col-md-3 col-6">
            <h6 className="footer-col-title">Shop Categories</h6>
            <ul className="footer-link-list">
              <li><Link to="/products?category=skincare">Skincare</Link></li>
              <li><Link to="/products?category=haircare">Haircare</Link></li>
              <li><Link to="/products?category=makeup">Makeup</Link></li>
              <li><Link to="/products?category=fragrance">Fragrance</Link></li>
              <li><Link to="/products?category=bodycare">Body Care</Link></li>
              <li><Link to="/products?category=nailcare">Nail Care</Link></li>
            </ul>
          </div>

          <div className="col-lg-3 col-md-3 col-6">
            <h6 className="footer-col-title">Discover By Concern</h6>
            <ul className="footer-link-list">
              <li><Link to="/products?concern=brightening">Brightening & Radiance</Link></li>
              <li><Link to="/products?concern=acne">Acne & Pore Care</Link></li>
              <li><Link to="/products?concern=hydration">Barrier & Hydration</Link></li>
              <li><Link to="/products?concern=frizz">Hair Repair & Frizz</Link></li>
              <li><Link to="/products?bestseller=true">Top Rated Bestsellers</Link></li>
              <li><Link to="/products?new=true">Fresh New Drops</Link></li>
            </ul>
          </div>

          <div className="col-lg-3 col-md-6">
            <h6 className="footer-col-title">About This Prototype</h6>
            <div className="prototype-info-card p-3">
              <p className="proto-text mb-2">
                <strong>Joyory SmartMatch</strong> is built for the Hackathon with full-stack Django REST Framework + React + SQLite.
              </p>
              <div className="proto-tech-stack">
                <span className="tech-tag">React 18</span>
                <span className="tech-tag">Django 5</span>
                <span className="tech-tag">DRF</span>
                <span className="tech-tag">SQLite</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom copyright */}
        <div className="footer-bottom-bar pt-4 border-top border-secondary-subtle d-flex flex-wrap align-items-center justify-content-between gap-3">
          <span className="footer-copy-text">
            © {new Date().getFullYear()} Joyory SmartMatch Prototype. Designed with passion for beauty science.
          </span>
          <span className="footer-disclaimer-text">
            <i className="bi bi-info-circle me-1"></i> Demo data for evaluation purposes.
          </span>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
