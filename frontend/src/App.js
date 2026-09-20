import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import ProductCatalog from './pages/ProductCatalog';
import ProductDetail from './pages/ProductDetail';
import SmartMatchQuiz from './pages/SmartMatchQuiz';
import ComparePage from './pages/ComparePage';
import WishlistPage from './pages/WishlistPage';
import CartPage from './pages/CartPage';
import CompareDock from './components/CompareDock';
import FaqAssistant from './components/FaqAssistant';
import { ShopProvider } from './context/ShopContext';
import './App.css';
import './theme-fixes.css';

function App() {
  return (
    <ShopProvider>
      <Router>
        <div className="App">
          <Navbar />
          <main className="app-main">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/products" element={<ProductCatalog />} />
              <Route path="/products/:id" element={<ProductDetail />} />
              <Route path="/quiz" element={<SmartMatchQuiz />} />
              <Route path="/smartmatch" element={<SmartMatchQuiz />} />
              <Route path="/compare" element={<ComparePage />} />
              <Route path="/wishlist" element={<WishlistPage />} />
              <Route path="/cart" element={<CartPage />} />
            </Routes>
          </main>
          <CompareDock />
          <FaqAssistant />
          <Footer />
        </div>
      </Router>
    </ShopProvider>
  );
}

export default App;
