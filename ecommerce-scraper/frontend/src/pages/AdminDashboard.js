/**
 * Admin Dashboard Page
 */

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import API from "../services/api";
import "./AdminDashboard.css";

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { user, isAdmin } = useAuth();
  
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mostWishlisted, setMostWishlisted] = useState([]);
  const [mostAlerted, setMostAlerted] = useState([]);
  const [recentNotifications, setRecentNotifications] = useState([]);
  const [runningEngine, setRunningEngine] = useState(false);

  useEffect(() => {
    if (!user || !isAdmin()) {
      navigate("/unauthorized");
      return;
    }
    fetchDashboardData();
  }, [user, isAdmin, navigate]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [dashRes, wishlistRes, alertedRes, notifRes] = await Promise.all([
        API.get("/admin/dashboard"),
        API.get("/admin/analytics/most-wishlisted?limit=5"),
        API.get("/admin/analytics/most-alerted?limit=5"),
        API.get("/admin/analytics/recent-notifications?limit=10")
      ]);
      
      setStats(dashRes.data);
      setMostWishlisted(wishlistRes.data);
      setMostAlerted(alertedRes.data);
      setRecentNotifications(notifRes.data);
    } catch (err) {
      console.error("Failed to fetch dashboard:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAlertEngine = async () => {
    if (!window.confirm("Run the alert engine now?")) return;
    
    setRunningEngine(true);
    try {
      const response = await API.post("/admin/run-alert-engine");
      alert(`Alert engine completed!\n\nChecked: ${response.data.results.alerts_checked}\nTriggered: ${response.data.results.alerts_triggered}\nEmails: ${response.data.results.emails_sent}`);
      fetchDashboardData();
    } catch (err) {
      alert("Failed to run alert engine: " + (err.response?.data?.detail || err.message));
    } finally {
      setRunningEngine(false);
    }
  };

  if (loading) {
    return (
      <div className="admin-dashboard">
        <div className="container py-5">
          <div className="loading-container">
            <div className="spinner-border text-warning"></div>
            <p>Loading dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="container py-4">
        {/* Header */}
        <div className="dashboard-header">
          <div>
            <h1>Admin Dashboard</h1>
            <p className="text-muted">Welcome back, {user?.name}</p>
          </div>
          <div className="header-actions">
            <button 
              className="btn btn-warning"
              onClick={handleRunAlertEngine}
              disabled={runningEngine}
            >
              {runningEngine ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2"></span>
                  Running...
                </>
              ) : (
                <>🔔 Run Alert Engine</>
              )}
            </button>
            <button 
              className="btn btn-outline-secondary"
              onClick={() => navigate("/admin/users")}
            >
              👥 Manage Users
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="stats-grid">
          {/* User Stats */}
          <div className="stat-card users">
            <div className="stat-icon">👥</div>
            <div className="stat-content">
              <h3>{stats?.user_metrics?.total_users || 0}</h3>
              <p>Total Users</p>
              <div className="stat-details">
                <span className="success">✓ {stats?.user_metrics?.verified_users || 0} verified</span>
                <span className="warning">○ {stats?.user_metrics?.unverified_users || 0} pending</span>
              </div>
            </div>
          </div>

          {/* Wishlist Stats */}
          <div className="stat-card wishlists">
            <div className="stat-icon">❤️</div>
            <div className="stat-content">
              <h3>{stats?.wishlist_metrics?.total_items || 0}</h3>
              <p>Wishlist Items</p>
              <div className="stat-details">
                <span>{stats?.wishlist_metrics?.users_with_wishlists || 0} users with wishlists</span>
              </div>
            </div>
          </div>

          {/* Alert Stats */}
          <div className="stat-card alerts">
            <div className="stat-icon">🔔</div>
            <div className="stat-content">
              <h3>{stats?.alert_metrics?.total_alerts || 0}</h3>
              <p>Price Alerts</p>
              <div className="stat-details">
                <span className="success">{stats?.alert_metrics?.active_alerts || 0} active</span>
                <span className="warning">{stats?.alert_metrics?.triggered_alerts || 0} triggered</span>
              </div>
            </div>
          </div>

          {/* Today Stats */}
          <div className="stat-card today">
            <div className="stat-icon">📧</div>
            <div className="stat-content">
              <h3>{stats?.alert_metrics?.emails_sent_today || 0}</h3>
              <p>Emails Today</p>
              <div className="stat-details">
                <span>{stats?.alert_metrics?.alerts_triggered_today || 0} alerts triggered</span>
              </div>
            </div>
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="dashboard-grid">
          {/* Most Wishlisted */}
          <div className="dashboard-card">
            <h3>❤️ Most Wishlisted Products</h3>
            <div className="product-list">
              {mostWishlisted.map((item, index) => (
                <div key={item.model_id} className="product-item">
                  <span className="rank">#{index + 1}</span>
                  <div className="product-info">
                    <p className="product-name">{item.product_name || item.model_id}</p>
                    <p className="product-brand">{item.brand}</p>
                  </div>
                  <span className="count">{item.wishlist_count} ❤️</span>
                </div>
              ))}
              {mostWishlisted.length === 0 && (
                <p className="empty-text">No wishlist data yet</p>
              )}
            </div>
          </div>

          {/* Most Alerted */}
          <div className="dashboard-card">
            <h3>🔔 Most Alerted Products</h3>
            <div className="product-list">
              {mostAlerted.map((item, index) => (
                <div key={item.model_id} className="product-item">
                  <span className="rank">#{index + 1}</span>
                  <div className="product-info">
                    <p className="product-name">{item.product_name || item.model_id}</p>
                    <p className="product-brand">{item.brand}</p>
                  </div>
                  <span className="count">{item.alert_count} 🔔</span>
                </div>
              ))}
              {mostAlerted.length === 0 && (
                <p className="empty-text">No alert data yet</p>
              )}
            </div>
          </div>
        </div>

        {/* Recent Notifications */}
        <div className="dashboard-card full-width">
          <h3>📧 Recent Alert Notifications</h3>
          <div className="notifications-table">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>User</th>
                  <th>Target</th>
                  <th>Triggered At</th>
                  <th>Platform</th>
                  <th>Email</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {recentNotifications.map((notif) => (
                  <tr key={notif.id}>
                    <td className="product-cell">
                      {notif.product_name?.substring(0, 40) || notif.model_id}...
                    </td>
                    <td>{notif.user_name}</td>
                    <td>₹{notif.target_price?.toLocaleString()}</td>
                    <td className="price-cell">₹{notif.triggered_price?.toLocaleString()}</td>
                    <td><span className="platform-badge">{notif.platform}</span></td>
                    <td>
                      {notif.email_sent ? (
                        <span className="badge success">✓ Sent</span>
                      ) : (
                        <span className="badge warning">Pending</span>
                      )}
                    </td>
                    <td className="time-cell">
                      {new Date(notif.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
                {recentNotifications.length === 0 && (
                  <tr>
                    <td colSpan="7" className="empty-text">No notifications yet</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;