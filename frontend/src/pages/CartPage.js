import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useShop } from '../context/ShopContext';
import './CartPage.css';

function CartPage() {
  const { cart, updateQuantity, removeFromCart, clearCart, cartSubtotal, cartCount } = useShop();

  // Promo Code State
  const [promoCode, setPromoCode] = useState('');
  const [discountPercent, setDiscountPercent] = useState(0);
  const [promoError, setPromoError] = useState('');
  const [promoSuccess, setPromoSuccess] = useState('');

  // Checkout Modal State
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [checkoutStep, setCheckoutStep] = useState(1); // 1: Address, 2: Confirmation
  const [customerName, setCustomerName] = useState('Beauty Explorer');
  const [customerAddress, setCustomerAddress] = useState('123 Radiant Glow Way, Suite 4B');
  const [customerCity, setCustomerCity] = useState('Mumbai, 400001');
  const [paymentMethod, setPaymentMethod] = useState('cod');
  const [orderId, setOrderId] = useState('');

  // Calculations
  const discountAmount = (cartSubtotal * discountPercent) / 100;
  const shippingFee = cartSubtotal > 499 || cartSubtotal === 0 ? 0 : 50;
  const grandTotal = Math.max(0, cartSubtotal - discountAmount + shippingFee);

  const handleApplyPromo = (e) => {
    e.preventDefault();
    setPromoError('');
    setPromoSuccess('');

    const clean = promoCode.trim().toUpperCase();
    if (clean === 'SMART10' || clean === 'SMARTBEAUTY') {
      setDiscountPercent(10);
      setPromoSuccess('Promo applied! 10% beauty discount added.');
    } else if (clean === 'JOYORY20') {
      setDiscountPercent(20);
      setPromoSuccess('VIP Promo applied! 20% discount added.');
    } else {
      setPromoError('Invalid promo code. Try "SMART10" or "JOYORY20" for demo.');
    }
  };

  const handleStartCheckout = () => {
    setCheckoutStep(1);
    setIsCheckoutOpen(true);
  };

  const handlePlaceDemoOrder = (e) => {
    e.preventDefault();
    const mockId = 'JOY-' + Math.floor(100000 + Math.random() * 900000);
    setOrderId(mockId);
    setCheckoutStep(2);
    clearCart();
  };

  return (
    <div className="cart-page-wrapper">
      <div className="container">
        {/* Header */}
        <div className="cart-header glass-card p-4 p-md-5 mb-4">
          <div className="d-flex flex-wrap align-items-center justify-content-between gap-3">
            <div>
              <span className="badge-pill-glow badge-emerald mb-2">
                <i className="bi bi-bag-check-fill me-1"></i> Beauty Bag
              </span>
              <h1 className="cart-title mb-1">
                Shopping <span className="gradient-text">Bag</span>
              </h1>
              <p className="cart-sub mb-0">
                {cartCount} item{cartCount !== 1 ? 's' : ''} in your personalized beauty routine bag.
              </p>
            </div>
            {cart.length > 0 && (
              <button className="btn-glass" onClick={clearCart}>
                <i className="bi bi-trash me-1"></i> Empty Bag
              </button>
            )}
          </div>
        </div>

        {/* Free Shipping Progress */}
        {cart.length > 0 && (
          <div className="shipping-progress-banner glass-card p-3 mb-4">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="fs-85 fw-bold text-white">
                <i className="bi bi-truck me-2 text-primary-light"></i>
                {cartSubtotal >= 499 ? (
                  <span className="text-success-light">🎉 You qualified for Free Standard Delivery!</span>
                ) : (
                  <span>Add ₹{(499 - cartSubtotal).toFixed(0)} more for Free Shipping</span>
                )}
              </span>
              <span className="fs-8 text-muted">Threshold: ₹499</span>
            </div>
            <div className="progress-track-sm">
              <div
                className="progress-fill-sm"
                style={{ width: `${Math.min(100, (cartSubtotal / 499) * 100)}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Cart Contents */}
        {cart.length === 0 ? (
          <div className="cart-empty-card glass-card p-5 text-center mx-auto mb-5">
            <div className="empty-icon-circle-emerald mb-3">
              <i className="bi bi-bag"></i>
            </div>
            <h2 className="fw-bold mb-2">Your Beauty Bag is Empty</h2>
            <p className="text-muted mb-4 max-w-450 mx-auto">
              Your bag looks a bit lonely. Explore our science-backed formulations or take the SmartMatch Quiz.
            </p>
            <div className="d-flex justify-content-center gap-3">
              <Link to="/products" className="btn-glow">
                <i className="bi bi-grid-3x3-gap me-2"></i> Browse All Products
              </Link>
              <Link to="/quiz" className="btn-glass">
                <i className="bi bi-magic me-2"></i> Take Match Quiz
              </Link>
            </div>
          </div>
        ) : (
          <div className="row g-4 mb-5">
            {/* Left: Cart Items List */}
            <div className="col-lg-8">
              <div className="cart-items-card glass-card p-4">
                <div className="table-responsive">
                  <table className="table cart-table text-white mb-0">
                    <thead>
                      <tr>
                        <th>Product</th>
                        <th className="text-center">Quantity</th>
                        <th className="text-end">Subtotal</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {cart.map((item) => {
                        const { product, quantity } = item;
                        const price = Number(product.discounted_price || product.price) || 0;
                        const itemSubtotal = price * quantity;

                        return (
                          <tr key={product.id}>
                            {/* Product Info */}
                            <td>
                              <div className="d-flex align-items-center gap-3">
                                <img
                                  src={product.image_url}
                                  alt={product.name}
                                  className="cart-item-thumbnail"
                                />
                                <div>
                                  <span className="cart-item-cat text-primary-light">{product.category}</span>
                                  <h6 className="cart-item-name mb-1">
                                    <Link to={`/products/${product.id}`} className="text-white text-decoration-none">
                                      {product.name}
                                    </Link>
                                  </h6>
                                  <span className="cart-item-brand">{product.brand}</span>
                                  <div className="cart-item-unit-price mt-1">
                                    <span>₹{price}</span>
                                    {product.discount_percent > 0 && (
                                      <span className="cart-unit-strike ms-2">₹{product.price}</span>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </td>

                            {/* Stepper Quantity */}
                            <td className="text-center align-middle">
                              <div className="quantity-stepper mx-auto">
                                <button
                                  className="btn-step"
                                  onClick={() => updateQuantity(product.id, quantity - 1)}
                                  title="Decrease quantity"
                                >
                                  <i className="bi bi-dash"></i>
                                </button>
                                <span className="qty-value">{quantity}</span>
                                <button
                                  className="btn-step"
                                  onClick={() => updateQuantity(product.id, quantity + 1)}
                                  title="Increase quantity"
                                >
                                  <i className="bi bi-plus"></i>
                                </button>
                              </div>
                            </td>

                            {/* Subtotal */}
                            <td className="text-end align-middle">
                              <span className="item-subtotal-val">₹{itemSubtotal.toFixed(0)}</span>
                            </td>

                            {/* Remove button */}
                            <td className="text-end align-middle">
                              <button
                                className="btn-cart-delete"
                                onClick={() => removeFromCart(product.id)}
                                title="Remove item"
                              >
                                <i className="bi bi-x-lg"></i>
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Right: Order Summary Sidebar */}
            <div className="col-lg-4">
              <div className="order-summary-card glass-card p-4">
                <h4 className="summary-heading mb-3">Order Summary</h4>

                {/* Subtotals */}
                <div className="summary-line d-flex justify-content-between mb-2">
                  <span className="text-muted">Bag Subtotal</span>
                  <span className="fw-bold">₹{cartSubtotal.toFixed(0)}</span>
                </div>

                {discountPercent > 0 && (
                  <div className="summary-line d-flex justify-content-between text-success-light mb-2">
                    <span>Promo Discount ({discountPercent}%)</span>
                    <span>-₹{discountAmount.toFixed(0)}</span>
                  </div>
                )}

                <div className="summary-line d-flex justify-content-between mb-2">
                  <span className="text-muted">Estimated Shipping</span>
                  <span>{shippingFee === 0 ? <span className="text-success-light">FREE</span> : `₹${shippingFee}`}</span>
                </div>

                <div className="summary-line d-flex justify-content-between mb-3">
                  <span className="text-muted">Estimated Taxes</span>
                  <span>₹0 (Demo)</span>
                </div>

                <div className="summary-divider border-top border-secondary-subtle pt-3 mb-4 d-flex justify-content-between align-items-baseline">
                  <span className="total-label">Grand Total</span>
                  <span className="total-amount">₹{grandTotal.toFixed(0)}</span>
                </div>

                {/* Promo Code Input */}
                <form onSubmit={handleApplyPromo} className="promo-box mb-4">
                  <label className="fs-8 text-dim d-block mb-1">Demo Promo Code:</label>
                  <div className="d-flex gap-2">
                    <input
                      type="text"
                      placeholder="e.g. SMART10"
                      value={promoCode}
                      onChange={(e) => setPromoCode(e.target.value)}
                      className="promo-input"
                    />
                    <button type="submit" className="btn-glass btn-sm">
                      Apply
                    </button>
                  </div>
                  {promoSuccess && <span className="fs-8 text-success-light d-block mt-1">{promoSuccess}</span>}
                  {promoError && <span className="fs-8 text-danger d-block mt-1">{promoError}</span>}
                </form>

                {/* Checkout CTA */}
                <button className="btn-glow btn-lg w-100 mb-3" onClick={handleStartCheckout}>
                  <i className="bi bi-shield-lock me-2"></i> Proceed to Demo Checkout
                </button>

                <div className="demo-badge-text text-center text-dim fs-8">
                  <i className="bi bi-info-circle me-1"></i> Simulated checkout for demonstration. No real card charge.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── Demo Checkout Modal ──────────────────────────────── */}
        {isCheckoutOpen && (
          <div className="checkout-modal-backdrop animate-in">
            <div className="checkout-modal-card glass-card p-4 p-md-5">
              <button className="btn-close-modal" onClick={() => setIsCheckoutOpen(false)}>
                <i className="bi bi-x-lg"></i>
              </button>

              {checkoutStep === 1 ? (
                <div>
                  <div className="text-center mb-4">
                    <span className="badge-pill-glow badge-violet mb-2">Simulated Hackathon Checkout</span>
                    <h3 className="modal-title">Review & Confirm Your Routine</h3>
                    <p className="modal-sub text-muted">Complete this quick form to preview your simulated order receipt.</p>
                  </div>

                  <form onSubmit={handlePlaceDemoOrder}>
                    <div className="row g-3 mb-3">
                      <div className="col-md-6">
                        <label className="modal-field-label">Recipient Name</label>
                        <input
                          type="text"
                          required
                          value={customerName}
                          onChange={(e) => setCustomerName(e.target.value)}
                          className="modal-input"
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="modal-field-label">Delivery Address</label>
                        <input
                          type="text"
                          required
                          value={customerAddress}
                          onChange={(e) => setCustomerAddress(e.target.value)}
                          className="modal-input"
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="modal-field-label">City & Pin Code</label>
                        <input
                          type="text"
                          required
                          value={customerCity}
                          onChange={(e) => setCustomerCity(e.target.value)}
                          className="modal-input"
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="modal-field-label">Demo Payment Method</label>
                        <select
                          className="modal-input"
                          value={paymentMethod}
                          onChange={(e) => setPaymentMethod(e.target.value)}
                        >
                          <option value="cod">Cash on Delivery (Simulated)</option>
                          <option value="upi">Demo UPI / Net Banking</option>
                          <option value="card">Demo Beauty Points</option>
                        </select>
                      </div>
                    </div>

                    <div className="modal-order-summary-mini p-3 glass-card mb-4">
                      <div className="d-flex justify-content-between mb-1 text-muted fs-85">
                        <span>Items ({cartCount}):</span>
                        <span>₹{cartSubtotal.toFixed(0)}</span>
                      </div>
                      {discountPercent > 0 && (
                        <div className="d-flex justify-content-between mb-1 text-success-light fs-85">
                          <span>Promo Savings:</span>
                          <span>-₹{discountAmount.toFixed(0)}</span>
                        </div>
                      )}
                      <div className="d-flex justify-content-between fw-bold pt-2 border-top border-secondary-subtle">
                        <span>Total Payable:</span>
                        <span className="text-success-light">₹{grandTotal.toFixed(0)}</span>
                      </div>
                    </div>

                    <div className="d-flex gap-3">
                      <button type="button" className="btn-glass flex-grow-1" onClick={() => setIsCheckoutOpen(false)}>
                        Cancel
                      </button>
                      <button type="submit" className="btn-glow btn-rose flex-grow-1">
                        <i className="bi bi-check-circle me-1"></i> Complete Demo Order
                      </button>
                    </div>
                  </form>
                </div>
              ) : (
                /* Step 2: Confirmation Receipt */
                <div className="text-center py-3">
                  <div className="order-success-icon mb-3">
                    <i className="bi bi-patch-check-fill text-success"></i>
                  </div>
                  <span className="badge-pill-glow badge-emerald mb-2">Order Confirmed!</span>
                  <h2 className="fw-bold mb-2">Thank You, {customerName}!</h2>
                  <p className="text-muted mb-4 max-w-450 mx-auto">
                    Your simulated beauty order has been successfully placed. Your formulas are being prepped for dispatch!
                  </p>

                  <div className="order-receipt-box glass-card p-3 mb-4 text-start max-w-450 mx-auto">
                    <div className="d-flex justify-content-between mb-2">
                      <span className="text-muted fs-85">Order Number:</span>
                      <strong className="text-primary-light">{orderId}</strong>
                    </div>
                    <div className="d-flex justify-content-between mb-2">
                      <span className="text-muted fs-85">Shipping Address:</span>
                      <span className="fs-85">{customerAddress}, {customerCity}</span>
                    </div>
                    <div className="d-flex justify-content-between mb-2">
                      <span className="text-muted fs-85">Estimated Delivery:</span>
                      <span className="fs-85 text-success">Within 2–3 Business Days</span>
                    </div>
                    <div className="d-flex justify-content-between pt-2 border-top border-secondary-subtle">
                      <span className="fw-bold">Total Amount:</span>
                      <strong className="text-success-light">₹{grandTotal.toFixed(0)}</strong>
                    </div>
                  </div>

                  <div className="d-flex justify-content-center gap-3">
                    <button className="btn-glow" onClick={() => setIsCheckoutOpen(false)}>
                      <i className="bi bi-bag me-1"></i> Continue Shopping
                    </button>
                    <Link to="/products" className="btn-glass" onClick={() => setIsCheckoutOpen(false)}>
                      Browse Catalog
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CartPage;
