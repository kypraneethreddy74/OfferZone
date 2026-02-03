/**
 * User Settings Page
 */

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { settingsAPI } from "../services/api";
import "./Settings.css";

const Settings = () => {
  const navigate = useNavigate();
  const { user, logout, isVerified } = useAuth();
  
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("profile");
  
  // Form states
  const [name, setName] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [deletePassword, setDeletePassword] = useState("");
  
  // Messages
  const [message, setMessage] = useState({ type: "", text: "" });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    fetchProfile();
  }, [user, navigate]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await settingsAPI.getProfile();
      setProfile(response.data);
      setName(response.data.name);
    } catch (err) {
      console.error("Failed to fetch profile:", err);
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: "", text: "" }), 5000);
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await settingsAPI.updateProfile({ name });
      showMessage("success", "Profile updated successfully");
      fetchProfile();
    } catch (err) {
      showMessage("error", err.response?.data?.detail || "Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      showMessage("error", "Passwords do not match");
      return;
    }
    
    setSaving(true);
    try {
      await settingsAPI.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword
      });
      showMessage("success", "Password changed successfully");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      showMessage("error", err.response?.data?.detail || "Failed to change password");
    } finally {
      setSaving(false);
    }
  };

  const handleDisableAllAlerts = async () => {
    if (!window.confirm("Disable all your price alerts?")) return;
    
    try {
      const response = await settingsAPI.disableAllAlerts();
      showMessage("success", response.data.message);
      fetchProfile();
    } catch (err) {
      showMessage("error", "Failed to disable alerts");
    }
  };

  const handleDeleteAllAlerts = async () => {
    if (!window.confirm("Delete ALL your price alerts? This cannot be undone.")) return;
    
    try {
      const response = await settingsAPI.deleteAllAlerts();
      showMessage("success", response.data.message);
      fetchProfile();
    } catch (err) {
      showMessage("error", "Failed to delete alerts");
    }
  };

  const handleClearWishlist = async () => {
    if (!window.confirm("Clear your entire wishlist? This cannot be undone.")) return;
    
    try {
      const response = await settingsAPI.clearWishlist();
      showMessage("success", response.data.message);
      fetchProfile();
    } catch (err) {
      showMessage("error", "Failed to clear wishlist");
    }
  };

  const handleExportData = async () => {
    try {
      const response = await settingsAPI.exportData();
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `offerzone-data-${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
      showMessage("success", "Data exported successfully");
    } catch (err) {
      showMessage("error", "Failed to export data");
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm("Are you sure you want to DELETE your account? This CANNOT be undone!")) return;
    if (!window.confirm("This will permanently delete all your data. Type your password to confirm.")) return;
    
    try {
      await settingsAPI.deleteAccount(deletePassword, true);
      alert("Account deleted successfully");
      logout();
      navigate("/");
    } catch (err) {
      showMessage("error", err.response?.data?.detail || "Failed to delete account");
    }
  };

  if (loading) {
    return (
      <div className="settings-page">
        <div className="container py-5">
          <div className="loading-container">
            <div className="spinner-border text-warning"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-page">
      <div className="container py-4">
        <h1 className="page-title">⚙️ Settings</h1>

        {/* Message */}
        {message.text && (
          <div className={`alert alert-${message.type === "success" ? "success" : "danger"}`}>
            {message.text}
          </div>
        )}

        <div className="settings-layout">
          {/* Sidebar */}
          <div className="settings-sidebar">
            <button
              className={`tab-btn ${activeTab === "profile" ? "active" : ""}`}
              onClick={() => setActiveTab("profile")}
            >
              👤 Profile
            </button>
            <button
              className={`tab-btn ${activeTab === "security" ? "active" : ""}`}
              onClick={() => setActiveTab("security")}
            >
              🔒 Security
            </button>
            <button
              className={`tab-btn ${activeTab === "alerts" ? "active" : ""}`}
              onClick={() => setActiveTab("alerts")}
            >
              🔔 Alerts
            </button>
            <button
              className={`tab-btn ${activeTab === "data" ? "active" : ""}`}
              onClick={() => setActiveTab("data")}
            >
              📦 Data & Privacy
            </button>
            <button
              className={`tab-btn danger ${activeTab === "danger" ? "active" : ""}`}
              onClick={() => setActiveTab("danger")}
            >
              ⚠️ Danger Zone
            </button>
          </div>

          {/* Content */}
          <div className="settings-content">
            {/* Profile Tab */}
            {activeTab === "profile" && (
              <div className="settings-card">
                <h2>Profile Information</h2>
                
                <div className="profile-header">
                  <div className="avatar">
                    {profile?.name?.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3>{profile?.name}</h3>
                    <p>{profile?.email}</p>
                    <span className={`badge ${profile?.is_verified ? "verified" : "unverified"}`}>
                      {profile?.is_verified ? "✓ Verified" : "○ Not Verified"}
                    </span>
                  </div>
                </div>

                <form onSubmit={handleUpdateProfile}>
                  <div className="form-group">
                    <label>Full Name</label>
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required
                      minLength={2}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Email</label>
                    <input type="email" value={profile?.email || ""} disabled />
                    <small>Email cannot be changed</small>
                  </div>

                  <button type="submit" className="btn btn-primary" disabled={saving}>
                    {saving ? "Saving..." : "Save Changes"}
                  </button>
                </form>

                <div className="stats-grid">
                  <div className="stat">
                    <span className="value">{profile?.stats?.wishlist_items || 0}</span>
                    <span className="label">Wishlist Items</span>
                  </div>
                  <div className="stat">
                    <span className="value">{profile?.stats?.total_alerts || 0}</span>
                    <span className="label">Total Alerts</span>
                  </div>
                  <div className="stat">
                    <span className="value">{profile?.stats?.active_alerts || 0}</span>
                    <span className="label">Active Alerts</span>
                  </div>
                </div>
              </div>
            )}

            {/* Security Tab */}
            {activeTab === "security" && (
              <div className="settings-card">
                <h2>🔒 Change Password</h2>
                
                <form onSubmit={handleChangePassword}>
                  <div className="form-group">
                    <label>Current Password</label>
                    <input
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>New Password</label>
                    <input
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      required
                      minLength={8}
                    />
                    <small>Minimum 8 characters with uppercase, lowercase, number & special character</small>
                  </div>
                  
                  <div className="form-group">
                    <label>Confirm New Password</label>
                    <input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                    />
                  </div>

                  <button type="submit" className="btn btn-primary" disabled={saving}>
                    {saving ? "Changing..." : "Change Password"}
                  </button>
                </form>
              </div>
            )}

            {/* Alerts Tab */}
            {activeTab === "alerts" && (
              <div className="settings-card">
                <h2>🔔 Alert Preferences</h2>
                
                <div className="alert-actions">
                  <div className="action-item">
                    <div>
                      <h4>Disable All Alerts</h4>
                      <p>Temporarily turn off all price notifications</p>
                    </div>
                    <button className="btn btn-outline-warning" onClick={handleDisableAllAlerts}>
                      Disable All
                    </button>
                  </div>
                  
                  <div className="action-item">
                    <div>
                      <h4>Delete All Alerts</h4>
                      <p>Permanently remove all your price alerts</p>
                    </div>
                    <button className="btn btn-outline-danger" onClick={handleDeleteAllAlerts}>
                      Delete All
                    </button>
                  </div>
                  
                  <div className="action-item">
                    <div>
                      <h4>Clear Wishlist</h4>
                      <p>Remove all items from your wishlist</p>
                    </div>
                    <button className="btn btn-outline-danger" onClick={handleClearWishlist}>
                      Clear Wishlist
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Data & Privacy Tab */}
            {activeTab === "data" && (
              <div className="settings-card">
                <h2>📦 Data & Privacy</h2>
                
                <div className="action-item">
                  <div>
                    <h4>Export Your Data</h4>
                    <p>Download all your data (profile, wishlist, alerts)</p>
                  </div>
                  <button className="btn btn-primary" onClick={handleExportData}>
                    📥 Export Data
                  </button>
                </div>
                
                <div className="privacy-info">
                  <h4>What data we collect:</h4>
                  <ul>
                    <li>Account information (name, email)</li>
                    <li>Wishlist items</li>
                    <li>Price alert settings</li>
                    <li>Login sessions</li>
                  </ul>
                  
                  <h4>How we use it:</h4>
                  <ul>
                    <li>Send price drop notifications</li>
                    <li>Personalize your experience</li>
                    <li>Improve our service</li>
                  </ul>
                </div>
              </div>
            )}

            {/* Danger Zone Tab */}
            {activeTab === "danger" && (
              <div className="settings-card danger-zone">
                <h2>⚠️ Danger Zone</h2>
                
                <div className="danger-warning">
                  <p>These actions are permanent and cannot be undone.</p>
                </div>
                
                <div className="action-item">
                  <div>
                    <h4>Delete Account</h4>
                    <p>Permanently delete your account and all associated data</p>
                  </div>
                  <div className="delete-form">
                    <input
                      type="password"
                      placeholder="Enter password to confirm"
                      value={deletePassword}
                      onChange={(e) => setDeletePassword(e.target.value)}
                    />
                    <button
                      className="btn btn-danger"
                      onClick={handleDeleteAccount}
                      disabled={!deletePassword}
                    >
                      🗑️ Delete My Account
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;