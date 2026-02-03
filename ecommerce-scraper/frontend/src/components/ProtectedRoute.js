/**
 * Protected Route Component
 * Handles authentication, verification, and admin checks
 */

import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ProtectedRoute = ({ 
  children, 
  requireVerified = false, 
  requireAdmin = false 
}) => {
  const { user, loading, isVerified, isAdmin } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking auth
  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: "50vh" }}>
        <div className="spinner-border text-warning" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  // Not authenticated - redirect to login
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Requires admin but user is not admin
  if (requireAdmin && !isAdmin()) {
    return <Navigate to="/unauthorized" replace />;
  }

  // Requires verification but user is not verified
  if (requireVerified && !isVerified()) {
    return (
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-md-6">
            <div className="card shadow-sm">
              <div className="card-body text-center p-5">
                <div className="mb-4">
                  <i className="bi bi-envelope-exclamation text-warning" style={{ fontSize: "4rem" }}></i>
                </div>
                <h3 className="mb-3">Email Verification Required</h3>
                <p className="text-muted mb-4">
                  You need to verify your email address to access this feature.
                </p>
                <div className="d-flex justify-content-center gap-3">
                  <a href="/resend-verification" className="btn btn-primary">
                    <i className="bi bi-envelope me-2"></i>
                    Resend Verification
                  </a>
                  <a href="/" className="btn btn-outline-secondary">
                    <i className="bi bi-house me-2"></i>
                    Go Home
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // All checks passed - render children
  return children;
};

export default ProtectedRoute;