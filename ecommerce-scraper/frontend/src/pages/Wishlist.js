/**
 * Wishlist Page with Price Alert Button
 */

import React, { useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useWishlist } from "../context/WishlistContext";
import WishlistButton from "../components/WishlistButton";
import PriceAlertButton from "../components/PriceAlertButton";  // ADD THIS
import "./Wishlist.css";

const Wishlist = () => {
  const navigate = useNavigate();
  const { user, isVerified } = useAuth();
  const { wishlist, loading, fetchWishlist } = useWishlist();

  useEffect(() => {
    if (user) {
      fetchWishlist();
    }
  }, [user, fetchWishlist]);

  // Not logged in
  if (!user) {
    return (
      <div className="wishlist-page">
        <div className="container py-5">
          <div className="empty-state">
            <span className="empty-icon">🔒</span>
            <h3>Login Required</h3>
            <p>Please login to view your wishlist</p>
            <Link to="/login" className="btn btn-primary">Login</Link>
          </div>
        </div>
      </div>
    );
  }

  // Loading
  if (loading) {
    return (
      <div className="wishlist-page">
        <div className="container py-5">
          <div className="loading-container">
            <div className="spinner-border text-warning" role="status"></div>
            <p>Loading your wishlist...</p>
          </div>
        </div>
      </div>
    );
  }

  // Empty wishlist
  if (wishlist.length === 0) {
    return (
      <div className="wishlist-page">
        <div className="container py-5">
          <h1 className="page-title">❤️ My Wishlist</h1>
          <div className="empty-state">
            <span className="empty-icon">💔</span>
            <h3>Your wishlist is empty</h3>
            <p>Start adding products you love!</p>
            <Link to="/best-deals" className="btn btn-primary">Browse Deals</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="wishlist-page">
      <div className="container py-4">
        <div className="page-header">
          <h1 className="page-title">❤️ My Wishlist</h1>
          <span className="item-count">{wishlist.length} items</span>
        </div>

        {/* Verification Warning */}
        {!isVerified() && (
          <div className="alert alert-warning mb-4">
            <i className="bi bi-exclamation-triangle me-2"></i>
            <strong>Verify your email</strong> to enable price alerts for your wishlist items.
            <Link to="/resend-verification" className="alert-link ms-2">
              Resend verification
            </Link>
          </div>
        )}

        <div className="wishlist-grid">
          {wishlist.map((item) => (
            <div key={item.id} className="wishlist-card">
              {/* Image */}
              <div className="card-image" onClick={() => navigate(`/compare/${item.model_id}`)}>
                {item.image_url ? (
                  <img src={item.image_url} alt={item.product_name} />
                ) : (
                  <div className="placeholder-image">📺</div>
                )}
              </div>
              
              {/* Content */}
              <div className="card-content">
                <h3 
                  className="product-name"
                  onClick={() => navigate(`/compare/${item.model_id}`)}
                >
                  {item.product_name || item.model_id}
                </h3>
                
                <p className="brand">{item.brand}</p>
                
                <div className="price-info">
                  {item.min_price && (
                    <span className="price">
                      ₹{item.min_price.toLocaleString("en-IN")}
                    </span>
                  )}
                  {item.max_discount > 0 && (
                    <span className="discount">{item.max_discount}% off</span>
                  )}
                </div>
                
                <p className="platforms">
                  Available on {item.platform_count} platform{item.platform_count !== 1 ? "s" : ""}
                </p>
                
                {/* Action Buttons */}
                <div className="card-actions">
                  <button
                    className="btn btn-outline-primary btn-sm"
                    onClick={() => navigate(`/compare/${item.model_id}`)}
                  >
                    🔍 Compare Prices
                  </button>
                  
                  <button
                    className="btn btn-outline-success btn-sm"
                    onClick={() => navigate(`/price-history/${item.model_id}`)}
                  >
                    📈 Price History
                  </button>
                </div>

                {/* ========== ADD THIS: Price Alert Button ========== */}
                <div className="alert-action mt-3">
                  <PriceAlertButton 
                    modelId={item.model_id}
                    currentPrice={item.min_price}
                    productName={item.product_name}
                  />
                </div>
                {/* ================================================== */}

                {/* Wishlist Button */}
                <div className="wishlist-action">
                  <WishlistButton modelId={item.model_id} size="sm" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Wishlist;