/**
 * Main App Component - OfferZone TV Price Intelligence
 * Complete routing with authentication and verification
 */

import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { WishlistProvider } from "./context/WishlistContext";

/* Layout */
import Navbar from "./components/Navbar";
import VerificationBanner from "./components/VerificationBanner";
import ProtectedRoute from "./components/ProtectedRoute";

/* Auth */
import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyEmail from "./pages/VerifyEmail";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import ResendVerification from "./pages/ResendVerification";
import Unauthorized from "./pages/Unauthorized";

/* Public */
import BestDeals from "./pages/BestDeals";
import Catalog from "./pages/Catalog";
import Products from "./pages/Products";
import Compare from "./pages/Compare";
import CompareResult from "./pages/CompareResult";
import Filters from "./pages/Filters";
import Brands from "./pages/Brands";
import BrandDetails from "./pages/BrandDetails";
import TVDetails from "./pages/TVDetails";
import PriceHistoryPage from "./pages/PriceHistoryPage";
import Graphs from "./pages/Graphs";
import BrandGraphs from "./pages/BrandGraphs";
import PlatformGraphs from "./pages/PlatformGraphs";
import Statistics from "./pages/Statistics";
import Home from "./pages/Home";

/* Real Feature Pages */
import Wishlist from "./pages/Wishlist";
import Alerts from "./pages/Alerts";
import Settings from "./pages/Settings";
import AdminDashboard from "./pages/AdminDashboard";
import AdminUsers from "./pages/AdminUsers";

import "./App.css";

function App() {
  return (
    <AuthProvider>
      <WishlistProvider>
        <Router>
          <Navbar />
          <VerificationBanner />

          <main className="main-content">
            <Routes>

              {/* PUBLIC */}
			  <Route path="/" element={<Home />} />

              {/*<Route path="/" element={<BestDeals />} /> */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/verify-email" element={<VerifyEmail />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/resend-verification" element={<ResendVerification />} />
              <Route path="/unauthorized" element={<Unauthorized />} />

              <Route path="/best-deals" element={<BestDeals />} />
              <Route path="/catalog" element={<Catalog />} />
              <Route path="/products" element={<Products />} />
              <Route path="/filters" element={<Filters />} />

              <Route path="/brands" element={<Brands />} />
              <Route path="/brands/:brandName" element={<BrandDetails />} />

              <Route path="/compare" element={<Compare />} />
              <Route path="/compare/:modelId" element={<CompareResult />} />

              <Route path="/tv/:modelId" element={<TVDetails />} />
              <Route path="/product/:modelId" element={<TVDetails />} />

              <Route path="/price-history/:modelId" element={<PriceHistoryPage />} />

              <Route path="/graphs" element={<Graphs />} />
              <Route path="/brand-graphs" element={<BrandGraphs />} />
              <Route path="/brand-graphs/:brandName" element={<BrandGraphs />} />
              <Route path="/platform-graphs" element={<PlatformGraphs />} />
              <Route path="/platform-graphs/:platformName" element={<PlatformGraphs />} />
              <Route path="/statistics" element={<Statistics />} />

              {/* USER */}
              <Route path="/wishlist" element={<ProtectedRoute><Wishlist /></ProtectedRoute>} />
              <Route path="/alerts" element={<ProtectedRoute requireVerified><Alerts /></ProtectedRoute>} />
              <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />

              {/* ADMIN */}
              <Route path="/admin" element={<ProtectedRoute requireAdmin><AdminDashboard /></ProtectedRoute>} />
              <Route path="/admin/users" element={<ProtectedRoute requireAdmin><AdminUsers /></ProtectedRoute>} />

              {/* FALLBACK */}
              <Route path="/404" element={<NotFound />} />
              <Route path="*" element={<Navigate to="/404" replace />} />

            </Routes>
          </main>
        </Router>
      </WishlistProvider>
    </AuthProvider>
  );
}

/* 404 */
const NotFound = () => (
  <div className="container py-5 text-center">
    <h1>404</h1>
    <p>Page not found</p>
  </div>
);

export default App;
