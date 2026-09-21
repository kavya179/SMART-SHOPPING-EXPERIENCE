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
import IngredientChecker from './pages/IngredientChecker';
import RoutineBuilder from './pages/RoutineBuilder';
import ReviewInsights from './pages/ReviewInsights';
import Dashboard from './pages/Dashboard';
import CompareDock from './components/CompareDock';
import FaqAssistant from './components/FaqAssistant';
import { ShopProvider } from './context/ShopContext';
import './App.css';
import './theme-fixes.css';
import './text-layout-fixes.css';
import './page-polish.css';

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
              <Route path="/ingredient-check" element={<IngredientChecker />} />
              <Route path="/routine" element={<RoutineBuilder />} />
              <Route path="/reviews" element={<ReviewInsights />} />
              <Route path="/dashboard" element={<Dashboard />} />
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
