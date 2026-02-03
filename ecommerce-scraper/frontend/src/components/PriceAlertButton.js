/**
 * Price Alert Button & Modal Component
 */

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { alertsAPI } from "../services/api";
import "./PriceAlertButton.css";

const PriceAlertButton = ({ modelId, currentPrice, productName }) => {
  const navigate = useNavigate();
  const { user, isVerified } = useAuth();
  
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [checkingStatus, setCheckingStatus] = useState(true);
  const [alertStatus, setAlertStatus] = useState(null);
  const [targetPrice, setTargetPrice] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Check alert status on mount
  useEffect(() => {
    if (user && modelId) {
      checkAlertStatus();
    } else {
      setCheckingStatus(false);
    }
  }, [user, modelId]);

  const checkAlertStatus = async () => {
    try {
      setCheckingStatus(true);
      const response = await alertsAPI.checkStatus(modelId);
      setAlertStatus(response.data);
      if (response.data.target_price) {
        setTargetPrice(response.data.target_price.toString());
      }
    } catch (err) {
      console.error("Failed to check alert status:", err);
    } finally {
      setCheckingStatus(false);
    }
  };

  const handleClick = (e) => {
    e.stopPropagation();
    e.preventDefault();

    if (!user) {
      navigate("/login", { state: { from: window.location.pathname } });
      return;
    }

    if (!isVerified()) {
      setError("Please verify your email to set price alerts");
      setShowModal(true);
      return;
    }

    // Set default target price (10% below current)
    if (!alertStatus?.has_alert && currentPrice) {
      setTargetPrice(Math.floor(currentPrice * 0.9).toString());
    }
    
    setShowModal(true);
    setError("");
    setSuccess("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    const price = parseFloat(targetPrice);
    if (isNaN(price) || price <= 0) {
      setError("Please enter a valid price");
      return;
    }

    setLoading(true);

    try {
      if (alertStatus?.has_alert) {
        // Update existing alert
        await alertsAPI.updateAlert(alertStatus.alert_id, { target_price: price });
        setSuccess("Alert updated successfully!");
      } else {
        // Create new alert
        const response = await alertsAPI.createAlert(modelId, price);
        setSuccess(response.data.message || "Alert created successfully!");
      }
      
      await checkAlertStatus();
      setTimeout(() => setShowModal(false), 1500);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save alert");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!alertStatus?.alert_id) return;
    
    setLoading(true);
    try {
      await alertsAPI.deleteAlert(alertStatus.alert_id);
      setAlertStatus({ has_alert: false });
      setTargetPrice("");
      setSuccess("Alert removed");
      setTimeout(() => setShowModal(false), 1000);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to remove alert");
    } finally {
      setLoading(false);
    }
  };

  const hasAlert = alertStatus?.has_alert;

  return (
    <>
      {/* Alert Button */}
      <button
        className={`price-alert-btn ${hasAlert ? "active" : ""} ${checkingStatus ? "loading" : ""}`}
        onClick={handleClick}
        disabled={checkingStatus}
        title={hasAlert ? `Alert set at ₹${alertStatus?.target_price?.toLocaleString()}` : "Set Price Alert"}
      >
        {checkingStatus ? (
          <span className="spinner-border spinner-border-sm"></span>
        ) : (
          <>
            <span className="alert-icon">{hasAlert ? "🔔" : "🔕"}</span>
            <span className="alert-text">
              {hasAlert ? `Alert: ₹${alertStatus?.target_price?.toLocaleString("en-IN")}` : "Set Price Alert"}
            </span>
          </>
        )}
      </button>

      {/* Modal */}
      {showModal && (
        <div className="alert-modal-overlay" onClick={() => setShowModal(false)}>
          <div className="alert-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowModal(false)}>
              ✕
            </button>

            <div className="modal-header">
              <span className="modal-icon">🔔</span>
              <h3>{hasAlert ? "Edit Price Alert" : "Set Price Alert"}</h3>
            </div>

            {productName && (
              <p className="product-name-modal">{productName}</p>
            )}

            {currentPrice && (
              <div className="current-price-info">
                <span className="label">Current Price:</span>
                <span className="price">₹{currentPrice.toLocaleString("en-IN")}</span>
              </div>
            )}

            {error && (
              <div className="alert-error">
                <i className="bi bi-exclamation-circle me-2"></i>
                {error}
              </div>
            )}

            {success && (
              <div className="alert-success">
                <i className="bi bi-check-circle me-2"></i>
                {success}
              </div>
            )}

            {!success && user && isVerified() && (
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label>Alert me when price drops to:</label>
                  <div className="price-input-wrapper">
                    <span className="currency">₹</span>
                    <input
                      type="number"
                      value={targetPrice}
                      onChange={(e) => setTargetPrice(e.target.value)}
                      placeholder="Enter target price"
                      min="1"
                      step="1"
                      disabled={loading}
                      autoFocus
                    />
                  </div>
                </div>

                {currentPrice && targetPrice && (
                  <p className="savings-preview">
                    {parseFloat(targetPrice) < currentPrice ? (
                      <>
                        💰 You'll save ₹{(currentPrice - parseFloat(targetPrice)).toLocaleString("en-IN")} 
                        ({Math.round((1 - parseFloat(targetPrice) / currentPrice) * 100)}% off)
                      </>
                    ) : parseFloat(targetPrice) === currentPrice ? (
                      <span className="info">ℹ️ Target equals current price</span>
                    ) : (
                      <span className="success">✅ Price already below target! You'll be notified immediately.</span>
                    )}
                  </p>
                )}

                <div className="modal-actions">
                  <button
                    type="submit"
                    className="btn-primary-modal"
                    disabled={loading || !targetPrice}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Saving...
                      </>
                    ) : (
                      hasAlert ? "Update Alert" : "Create Alert"
                    )}
                  </button>

                  {hasAlert && (
                    <button
                      type="button"
                      className="btn-danger-modal"
                      onClick={handleDelete}
                      disabled={loading}
                    >
                      Remove Alert
                    </button>
                  )}
                </div>
              </form>
            )}

            {!user && (
              <div className="modal-login-prompt">
                <p>Please login to set price alerts</p>
                <button 
                  onClick={() => {
                    setShowModal(false);
                    navigate("/login");
                  }} 
                  className="btn-primary-modal"
                >
                  Login
                </button>
              </div>
            )}

            {user && !isVerified() && (
              <div className="modal-verify-prompt">
                <p>Please verify your email to set price alerts</p>
                <button 
                  onClick={() => {
                    setShowModal(false);
                    navigate("/resend-verification");
                  }} 
                  className="btn-primary-modal"
                >
                  Resend Verification Email
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default PriceAlertButton;