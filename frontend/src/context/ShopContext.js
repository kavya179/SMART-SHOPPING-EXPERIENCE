import React, { createContext, useContext, useState, useEffect } from 'react';

const ShopContext = createContext();

export function useShop() {
  const context = useContext(ShopContext);
  if (!context) {
    throw new Error('useShop must be used within a ShopProvider');
  }
  return context;
}

export function ShopProvider({ children }) {
  // ── Wishlist State (localStorage persisted) ───────────────────
  const [wishlist, setWishlist] = useState(() => {
    try {
      const saved = localStorage.getItem('joyory_wishlist');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // ── Cart State (localStorage persisted) ───────────────────────
  const [cart, setCart] = useState(() => {
    try {
      const saved = localStorage.getItem('joyory_cart');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // ── Compare List State (max 3 items) ─────────────────────────
  const [compareList, setCompareList] = useState(() => {
    try {
      const saved = localStorage.getItem('joyory_compare');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // ── Toast Notification State ─────────────────────────────────
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => {
      setToast(null);
    }, 3000);
  };

  // Sync to localStorage
  useEffect(() => {
    localStorage.setItem('joyory_wishlist', JSON.stringify(wishlist));
  }, [wishlist]);

  useEffect(() => {
    localStorage.setItem('joyory_cart', JSON.stringify(cart));
  }, [cart]);

  useEffect(() => {
    localStorage.setItem('joyory_compare', JSON.stringify(compareList));
  }, [compareList]);

  // ── Wishlist Methods ──────────────────────────────────────────
  const toggleWishlist = (product) => {
    setWishlist((prev) => {
      const exists = prev.some((item) => item.id === product.id);
      if (exists) {
        showToast(`Removed "${product.name}" from your wishlist.`, 'info');
        return prev.filter((item) => item.id !== product.id);
      } else {
        showToast(`Saved "${product.name}" to your wishlist! ❤️`);
        return [...prev, product];
      }
    });
  };

  const isInWishlist = (productId) => {
    return wishlist.some((item) => item.id === productId);
  };

  const removeFromWishlist = (productId) => {
    setWishlist((prev) => prev.filter((item) => item.id !== productId));
    showToast('Item removed from wishlist.', 'info');
  };

  // ── Cart Methods ──────────────────────────────────────────────
  const addToCart = (product, quantity = 1) => {
    setCart((prev) => {
      const existingIndex = prev.findIndex((item) => item.product.id === product.id);
      if (existingIndex > -1) {
        const updated = [...prev];
        updated[existingIndex].quantity += quantity;
        showToast(`Updated quantity for "${product.name}" in bag (${updated[existingIndex].quantity})! ✨`);
        return updated;
      } else {
        showToast(`Added "${product.name}" to your Beauty Bag! 🛍️`);
        return [...prev, { product, quantity }];
      }
    });
  };

  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }
    setCart((prev) =>
      prev.map((item) =>
        item.product.id === productId ? { ...item, quantity: newQuantity } : item
      )
    );
  };

  const removeFromCart = (productId) => {
    setCart((prev) => prev.filter((item) => item.product.id !== productId));
    showToast('Item removed from Beauty Bag.', 'info');
  };

  const clearCart = () => {
    setCart([]);
  };

  // Cart Calculations
  const cartSubtotal = cart.reduce((sum, item) => {
    const price = Number(item.product.discounted_price || item.product.price) || 0;
    return sum + price * item.quantity;
  }, 0);

  const cartCount = cart.reduce((count, item) => count + item.quantity, 0);

  // ── Compare Methods (Max 3 items) ─────────────────────────────
  const toggleCompare = (product) => {
    setCompareList((prev) => {
      const exists = prev.some((item) => item.id === product.id);
      if (exists) {
        showToast(`Removed "${product.name}" from comparison.`, 'info');
        return prev.filter((item) => item.id !== product.id);
      } else {
        if (prev.length >= 3) {
          showToast('You can compare up to 3 products at a time.', 'warning');
          return prev;
        }
        showToast(`Added "${product.name}" to comparison (${prev.length + 1}/3)! ⚖️`);
        return [...prev, product];
      }
    });
  };

  const isInCompare = (productId) => {
    return compareList.some((item) => item.id === productId);
  };

  const removeFromCompare = (productId) => {
    setCompareList((prev) => prev.filter((item) => item.id !== productId));
  };

  const clearCompare = () => {
    setCompareList([]);
  };

  return (
    <ShopContext.Provider
      value={{
        wishlist,
        toggleWishlist,
        isInWishlist,
        removeFromWishlist,
        cart,
        addToCart,
        updateQuantity,
        removeFromCart,
        clearCart,
        cartSubtotal,
        cartCount,
        compareList,
        toggleCompare,
        isInCompare,
        removeFromCompare,
        clearCompare,
        showToast,
      }}
    >
      {children}

      {/* Global Toast Micro-Notification */}
      {toast && (
        <div className={`shop-toast-notification toast-${toast.type} animate-in`}>
          <i
            className={`bi ${
              toast.type === 'warning'
                ? 'bi-exclamation-circle'
                : toast.type === 'info'
                ? 'bi-info-circle'
                : 'bi-check2-circle'
            } me-2`}
          ></i>
          <span>{toast.message}</span>
        </div>
      )}
    </ShopContext.Provider>
  );
}
