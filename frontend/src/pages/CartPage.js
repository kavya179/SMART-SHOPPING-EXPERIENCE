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

  // Checkout & Order Modal State
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [customerName, setCustomerName] = useState('Beauty Explorer');
  const [customerPhone, setCustomerPhone] = useState('+91 98765 43210');
  const [customerAddress, setCustomerAddress] = useState('123 Radiant Glow Way, Suite 4B');
  const [customerCity, setCustomerCity] = useState('Mumbai, 400001');
  const [paymentMethod, setPaymentMethod] = useState('cod');
  const [completedOrder, setCompletedOrder] = useState(null);

  // Calculations
  const discountAmount = (cartSubtotal * discountPercent) / 100;
  const shippingFee = cartSubtotal > 499 || cartSubtotal === 0 ? 0 : 50;
  const taxAmount = (cartSubtotal * 0.18) / 1.18; // 18% inclusive GST
  const grandTotal = Math.max(0, cartSubtotal - discountAmount + shippingFee);

  // Formatted current date and time
  const today = new Date();
  const currentDateStr = today.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
  const currentTimeStr = today.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
  });

  const estDeliveryDate = new Date(today);
  estDeliveryDate.setDate(today.getDate() + 3);
  const estDeliveryStr = estDeliveryDate.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });

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

  const handlePlaceOrder = (e) => {
    if (e) e.preventDefault();
    if (cart.length === 0) return;

    const mockId = 'JOY-' + Math.floor(100000 + Math.random() * 900000);
    const snapshot = {
      orderId: mockId,
      orderDate: `${currentDateStr}, ${currentTimeStr}`,
      estDelivery: estDeliveryStr,
      items: [...cart],
      cartCount,
      subtotal: cartSubtotal,
      discountPercent,
      discountAmount,
      shippingFee,
      taxAmount,
      grandTotal,
      customerName,
      customerPhone,
      customerAddress,
      customerCity,
      paymentMethod: paymentMethod === 'cod' ? 'Cash on Delivery (Simulated)' : paymentMethod === 'upi' ? 'Demo UPI / Net Banking' : 'Demo Beauty Points',
    };

    setCompletedOrder(snapshot);
    setIsCheckoutOpen(true);
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
                Shopping <span className="gradient-text">Bag & Bill</span>
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
              <span className="fs-85 fw-bold text-dark">
                <i className="bi bi-truck me-2 text-rose"></i>
                {cartSubtotal >= 499 ? (
                  <span className="text-success fw-bold">🎉 You qualified for Free Standard Delivery!</span>
                ) : (
                  <span>Add ₹{(499 - cartSubtotal).toFixed(0)} more for Free Shipping</span>
                )}
              </span>
              <span className="fs-8 text-muted">Free Shipping over ₹499</span>
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
        {cart.length === 0 && !completedOrder ? (
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
          <div className="cart-checkout-grid mb-5">
            {/* Left: Cart Items List & Delivery Form */}
            <div className="cart-main-col">
              <div className="cart-items-card p-4 mb-4">
                <h4 className="cart-card-heading mb-3">
                  <i className="bi bi-bag-heart me-2 text-rose"></i> Items in Your Routine ({cartCount})
                </h4>
                <div className="table-responsive">
                  <table className="table cart-table mb-0">
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
                                  src={product.image_url || 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80'}
                                  alt={product.name}
                                  className="cart-item-thumbnail"
                                  onError={(e) => {
                                    e.target.onerror = null;
                                    e.target.src = 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80';
                                  }}
                                />
                                <div>
                                  <span className="cart-item-cat">{product.category}</span>
                                  <h6 className="cart-item-name mb-1">
                                    <Link to={`/products/${product.id}`} className="cart-item-link">
                                      {product.name}
                                    </Link>
                                  </h6>
                                  <span className="cart-item-brand">{product.brand}</span>
                                  <div className="cart-item-unit-price mt-1">
                                    <span className="cart-price-active">₹{price}</span>
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
                                <i className="bi bi-trash"></i>
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Delivery Address & Customer Details Quick Form */}
              <div className="delivery-details-card p-4">
                <h4 className="cart-card-heading mb-3">
                  <i className="bi bi-geo-alt me-2 text-rose"></i> Shipping & Delivery Details
                </h4>
                <div className="row g-3">
                  <div className="col-md-6">
                    <label className="bill-input-label">Customer Name</label>
                    <input
                      type="text"
                      className="bill-text-input"
                      value={customerName}
                      onChange={(e) => setCustomerName(e.target.value)}
                      placeholder="e.g. Priya Sharma"
                    />
                  </div>
                  <div className="col-md-6">
                    <label className="bill-input-label">Contact Phone</label>
                    <input
                      type="text"
                      className="bill-text-input"
                      value={customerPhone}
                      onChange={(e) => setCustomerPhone(e.target.value)}
                      placeholder="e.g. +91 98765 43210"
                    />
                  </div>
                  <div className="col-md-8">
                    <label className="bill-input-label">Delivery Street Address</label>
                    <input
                      type="text"
                      className="bill-text-input"
                      value={customerAddress}
                      onChange={(e) => setCustomerAddress(e.target.value)}
                      placeholder="Flat, building, street area"
                    />
                  </div>
                  <div className="col-md-4">
                    <label className="bill-input-label">City & Pincode</label>
                    <input
                      type="text"
                      className="bill-text-input"
                      value={customerCity}
                      onChange={(e) => setCustomerCity(e.target.value)}
                      placeholder="City, Pincode"
                    />
                  </div>
                  <div className="col-12">
                    <label className="bill-input-label">Demo Payment Method</label>
                    <div className="payment-options-grid">
                      <label className={`payment-pill-opt ${paymentMethod === 'cod' ? 'active' : ''}`}>
                        <input
                          type="radio"
                          name="payment"
                          value="cod"
                          checked={paymentMethod === 'cod'}
                          onChange={() => setPaymentMethod('cod')}
                        />
                        <i className="bi bi-cash-coin me-2"></i> Cash on Delivery (Demo)
                      </label>
                      <label className={`payment-pill-opt ${paymentMethod === 'upi' ? 'active' : ''}`}>
                        <input
                          type="radio"
                          name="payment"
                          value="upi"
                          checked={paymentMethod === 'upi'}
                          onChange={() => setPaymentMethod('upi')}
                        />
                        <i className="bi bi-qr-code me-2"></i> Demo UPI / Net Banking
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right: Detailed Bill & Order Summary Card */}
            <div className="cart-sidebar-col">
              <div className="order-summary-card p-4">
                <div className="bill-top-header mb-3 pb-3">
                  <div className="d-flex justify-content-between align-items-center mb-1">
                    <h4 className="summary-heading mb-0">Order Bill Breakdown</h4>
                    <span className="badge-pill-glow badge-emerald">Verified Bill</span>
                  </div>
                  <span className="bill-meta-date text-muted">
                    <i className="bi bi-calendar3 me-1"></i> {currentDateStr} • {currentTimeStr}
                  </span>
                </div>

                {/* Delivery schedule pill */}
                <div className="delivery-badge-row mb-3 p-2 px-3">
                  <i className="bi bi-truck text-rose me-2"></i>
                  <span>Estimated Delivery: <strong>{estDeliveryStr}</strong></span>
                </div>

                {/* Line Items Breakdown */}
                <div className="bill-line-items mb-3">
                  <div className="bill-line-item">
                    <span className="line-label">Bag Subtotal ({cartCount} items)</span>
                    <span className="line-val">₹{cartSubtotal.toFixed(0)}</span>
                  </div>

                  {discountPercent > 0 && (
                    <div className="bill-line-item text-success">
                      <span className="line-label">Promo Discount ({discountPercent}% applied)</span>
                      <span className="line-val">-₹{discountAmount.toFixed(0)}</span>
                    </div>
                  )}

                  <div className="bill-line-item">
                    <span className="line-label">Standard Delivery</span>
                    <span className="line-val">
                      {shippingFee === 0 ? (
                        <span className="text-success fw-bold">FREE</span>
                      ) : (
                        <span>₹{shippingFee}</span>
                      )}
                    </span>
                  </div>

                  <div className="bill-line-item">
                    <span className="line-label">GST / Taxes (18% Included)</span>
                    <span className="line-val text-muted">₹{taxAmount.toFixed(0)}</span>
                  </div>
                </div>

                {/* Grand Total */}
                <div className="grand-total-box p-3 mb-4">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <span className="total-title d-block">Grand Total</span>
                      <span className="total-sub">Inclusive of all taxes</span>
                    </div>
                    <span className="total-amount-val">₹{grandTotal.toFixed(0)}</span>
                  </div>
                </div>

                {/* Promo Code Input */}
                <form onSubmit={handleApplyPromo} className="promo-box mb-4">
                  <label className="bill-input-label mb-1">Have a Coupon Code?</label>
                  <div className="promo-input-group">
                    <input
                      type="text"
                      placeholder="e.g. SMART10"
                      value={promoCode}
                      onChange={(e) => setPromoCode(e.target.value)}
                      className="promo-input"
                    />
                    <button type="submit" className="btn-promo-apply">
                      Apply
                    </button>
                  </div>
                  {promoSuccess && <span className="fs-8 text-success d-block mt-2 fw-semibold"><i className="bi bi-check-circle me-1"></i>{promoSuccess}</span>}
                  {promoError && <span className="fs-8 text-danger d-block mt-2"><i className="bi bi-exclamation-circle me-1"></i>{promoError}</span>}
                </form>

                {/* Checkout Button */}
                <button
                  className="btn-glow btn-place-order btn-lg w-100 mb-3"
                  onClick={handlePlaceOrder}
                  disabled={cart.length === 0}
                >
                  <i className="bi bi-shield-check me-2"></i> Place Demo Order (₹{grandTotal.toFixed(0)})
                </button>

                <div className="demo-badge-text text-center text-muted fs-8">
                  <i className="bi bi-info-circle me-1"></i> Simulated billing & order system. No real card charge required.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── Order Success Popup Modal ──────────────────────── */}
        {isCheckoutOpen && completedOrder && (
          <div className="order-success-modal-backdrop animate-in">
            <div className="order-success-card glass-card p-4 p-md-5">
              <button
                className="btn-close-modal"
                onClick={() => setIsCheckoutOpen(false)}
                title="Close"
              >
                <i className="bi bi-x-lg"></i>
              </button>

              <div className="text-center mb-4">
                <div className="success-badge-icon mb-3">
                  <i className="bi bi-check-circle-fill"></i>
                </div>
                <span className="badge-pill-glow badge-emerald mb-2">Order Confirmed!</span>
                <h2 className="success-order-title mb-1">Thank You, {completedOrder.customerName}!</h2>
                <p className="success-order-subtitle text-muted">
                  Your simulated beauty order has been successfully placed and recorded.
                </p>
              </div>

              {/* Bill & Receipt Details Box */}
              <div className="success-bill-receipt p-4 mb-4">
                <div className="receipt-header-row d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom">
                  <div>
                    <span className="receipt-label">Invoice Number</span>
                    <h5 className="receipt-val-bold mb-0">{completedOrder.orderId}</h5>
                  </div>
                  <div className="text-end">
                    <span className="receipt-label">Order Date & Time</span>
                    <span className="receipt-val d-block">{completedOrder.orderDate}</span>
                  </div>
                </div>

                <div className="row g-3 mb-3 pb-3 border-bottom">
                  <div className="col-sm-6">
                    <span className="receipt-label">Shipping Address</span>
                    <span className="receipt-val d-block">{completedOrder.customerAddress}, {completedOrder.customerCity}</span>
                    <span className="receipt-val text-muted">{completedOrder.customerPhone}</span>
                  </div>
                  <div className="col-sm-6 text-sm-end">
                    <span className="receipt-label">Payment Mode</span>
                    <span className="receipt-val d-block text-success fw-bold">{completedOrder.paymentMethod}</span>
                    <span className="receipt-label mt-2 d-block">Estimated Delivery</span>
                    <span className="receipt-val d-block">{completedOrder.estDelivery}</span>
                  </div>
                </div>

                {/* Ordered Items Table */}
                <div className="receipt-items-list mb-3">
                  <span className="receipt-label mb-2 d-block">Ordered Formulas ({completedOrder.cartCount} items):</span>
                  {completedOrder.items.map((item, i) => (
                    <div key={i} className="d-flex justify-content-between align-items-center py-2 border-bottom border-light-subtle">
                      <div className="d-flex align-items-center gap-2">
                        <span className="badge bg-light text-dark rounded-pill">x{item.quantity}</span>
                        <span className="receipt-item-name">{item.product.name}</span>
                      </div>
                      <span className="receipt-item-price fw-semibold">
                        ₹{((Number(item.product.discounted_price || item.product.price) || 0) * item.quantity).toFixed(0)}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Final Totals Breakdown */}
                <div className="receipt-totals-box pt-2">
                  <div className="d-flex justify-content-between py-1 text-muted fs-85">
                    <span>Subtotal:</span>
                    <span>₹{completedOrder.subtotal.toFixed(0)}</span>
                  </div>
                  {completedOrder.discountAmount > 0 && (
                    <div className="d-flex justify-content-between py-1 text-success fs-85">
                      <span>Promo Discount ({completedOrder.discountPercent}%):</span>
                      <span>-₹{completedOrder.discountAmount.toFixed(0)}</span>
                    </div>
                  )}
                  <div className="d-flex justify-content-between py-1 text-muted fs-85">
                    <span>Shipping:</span>
                    <span>{completedOrder.shippingFee === 0 ? 'FREE' : `₹${completedOrder.shippingFee}`}</span>
                  </div>
                  <div className="d-flex justify-content-between pt-2 border-top mt-2 fs-5 fw-bold">
                    <span>Total Amount Billed:</span>
                    <span className="text-rose">₹{completedOrder.grandTotal.toFixed(0)}</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="d-flex flex-wrap justify-content-center gap-3">
                <Link to="/products" className="btn-glow" onClick={() => setIsCheckoutOpen(false)}>
                  <i className="bi bi-grid-3x3-gap me-2"></i> Continue Shopping
                </Link>
                <button className="btn-glass" onClick={() => window.print()}>
                  <i className="bi bi-printer me-2"></i> Print Receipt
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CartPage;
