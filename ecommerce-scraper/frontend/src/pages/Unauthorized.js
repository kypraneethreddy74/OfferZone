/**
 * Unauthorized Access Page
 */

import React from "react";
import { Link } from "react-router-dom";
import "./Auth.css";

const Unauthorized = () => {
  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-form-container" style={{ flex: 1 }}>
          <div className="auth-card text-center">
            <div className="mb-4">
              <i className="bi bi-shield-x text-danger" style={{ fontSize: "5rem" }}></i>
            </div>
            <h2 className="mb-3">Access Denied</h2>
            <p className="text-muted mb-4">
              You don't have permission to access this page.
            </p>
            <div className="d-flex justify-content-center gap-3">
              <Link to="/" className="btn btn-primary btn-auth">
                <i className="bi bi-house me-2"></i>
                Go Home
              </Link>
              <Link to="/login" className="btn btn-outline-secondary">
                <i className="bi bi-box-arrow-in-right me-2"></i>
                Login
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Unauthorized;