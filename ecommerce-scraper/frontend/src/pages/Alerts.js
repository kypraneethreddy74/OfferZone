/**
 * Price Alerts Management Page
 */

import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { alertsAPI } from "../services/api";
import "./Alerts.css";

const Alerts = () => {
  const navigate = useNavigate();
  const { user, isVerified } = useAuth();
  
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, active: 0, triggered: 0 });
  const [editingId, setEditingId] = useState(null);
  const [editPrice, setEditPrice] = useState("");

  useEffect(() => {
    if (user) {
      fetchAlerts();
    }
  }, [user]);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await alertsAPI.getAlerts();
      setAlerts(response.data.alerts || []);
      setStats({
        total: response.data.total,
        active: response.data.active_count,
        triggered: response.data.triggered_count
      });
    } catch (err) {
      console.error("Failed to fetch alerts:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (alertId) => {
    try {
      await alertsAPI.toggleAlert(alertId);
      fetchAlerts();
    } catch (err) {
      console.error("Failed to toggle alert:", err);
    }
  };

  const handleDelete = async (alertId) => {
    if (!window.confirm("Remove this price alert?")) return;
    
    try {
      await alertsAPI.deleteAlert(alertId);
      fetchAlerts();
    } catch (err) {
      console.error("Failed to delete alert:", err);
    }
  };

  const handleEdit = (alert) => {
    setEditingId(alert.id);
    setEditPrice(alert.target_price.toString());
  };

  const handleSaveEdit = async (alertId) => {
    try {
      await alertsAPI.updateAlert(alertId, { target_price: parseFloat(editPrice) });
      setEditingId(null);
      fetchAlerts();
    } catch (err) {
      console.error("Failed to update alert:", err);
    }
  };

  // Not logged in
  if (!user) {
    return (
      <div className="alerts-page">
        <div className="container py-5">
          <div className="empty-state">
            <span className="empty-icon">🔒</span>
            <h3>Login Required</h3>
            <p>Please login to manage your price alerts</p>
            <Link to="/login" className="btn btn-primary">Login</Link>
          </div>
        </div>
      </div>
    );
  }

  // Not verified
  if (!isVerified()) {
    return (
      <div className="alerts-page">
        <div className="container py-5">
          <div className="empty-state">
            <span className="empty-icon">📧</span>
            <h3>Email Verification Required</h3>
            <p>Please verify your email to use price alerts</p>
            <Link to="/resend-verification" className="btn btn-primary">
              Resend Verification
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="alerts-page">
      <div className="container py-4">
        {/* Header */}
        <div className="page-header">
          <h1 className="page-title">
            <span>🔔</span> Price Alerts
          </h1>
          <div className="alert-stats">
            <span className="stat">
              <strong>{stats.total}</strong> Total
            </span>
            <span className="stat active">
              <strong>{stats.active}</strong> Active
            </span>
            <span className="stat triggered">
              <strong>{stats.triggered}</strong> Triggered
            </span>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="loading-container">
            <div className="spinner-border text-warning"></div>
            <p>Loading alerts...</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && alerts.length === 0 && (
          <div className="empty-state">
            <span className="empty-icon">🔕</span>
            <h3>No price alerts yet</h3>
            <p>Set alerts on products to get notified when prices drop!</p>
            <Link to="/best-deals" className="btn btn-primary">
              Browse Products
            </Link>
          </div>
        )}

        {/* Alerts List */}
        {!loading && alerts.length > 0 && (
          <div className="alerts-list">
            {alerts.map((alert) => (
              <div 
                key={alert.id} 
                className={`alert-card ${!alert.is_active ? "inactive" : ""} ${alert.is_triggered ? "triggered" : ""}`}
              >
                <div className="alert-image" onClick={() => navigate(`/compare/${alert.model_id}`)}>
                  {alert.image_url ? (
                    <img src={alert.image_url} alt={alert.product_name} />
                  ) : (
                    <div className="placeholder">📺</div>
                  )}
                </div>

                <div className="alert-content">
                  <h3 onClick={() => navigate(`/compare/${alert.model_id}`)}>
                    {alert.product_name || alert.model_id}
                  </h3>
                  <p className="brand">{alert.brand}</p>

                  <div className="price-info">
                    <div className="price-row">
                      <span className="label">Current:</span>
                      <span className="current-price">
                        ₹{alert.current_price?.toLocaleString("en-IN") || "N/A"}
                      </span>
                    </div>
                    <div className="price-row">
                      <span className="label">Target:</span>
                      {editingId === alert.id ? (
                        <div className="edit-price">
                          <input
                            type="number"
                            value={editPrice}
                            onChange={(e) => setEditPrice(e.target.value)}
                            autoFocus
                          />
                          <button onClick={() => handleSaveEdit(alert.id)}>✓</button>
                          <button onClick={() => setEditingId(null)}>✕</button>
                        </div>
                      ) : (
                        <span className="target-price" onClick={() => handleEdit(alert)}>
                          ₹{alert.target_price?.toLocaleString("en-IN")}
                          <i className="bi bi-pencil"></i>
                        </span>
                      )}
                    </div>
                  </div>

                  {alert.is_triggered && (
                    <div className="triggered-badge">
                      🎉 Price reached! ({alert.trigger_count}x)
                    </div>
                  )}
                </div>

                <div className="alert-actions">
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={alert.is_active}
                      onChange={() => handleToggle(alert.id)}
                    />
                    <span className="slider"></span>
                  </label>
                  
                  <button
                    className="btn-icon"
                    onClick={() => navigate(`/price-history/${alert.model_id}`)}
                    title="View Price History"
                  >
                    📈
                  </button>
                  
                  <button
                    className="btn-icon danger"
                    onClick={() => handleDelete(alert.id)}
                    title="Delete Alert"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Alerts;