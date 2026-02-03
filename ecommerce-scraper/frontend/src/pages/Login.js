/**
 * Login Page - Premium SaaS Design
 */

import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Auth.css";

const Login = () => {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { login, error, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setFormError("");
    clearError();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setFormError("");

    const result = await login(formData);
    
    if (result.success) {
      const from = location.state?.from?.pathname || "/";
      navigate(from, { replace: true });
    } else {
      setFormError(result.error);
    }
    
    setIsSubmitting(false);
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        {/* Left Side - Branding */}
        <div className="auth-branding">
          <div className="brand-content">
            <h1 className="brand-title">OfferZone</h1>
            <p className="brand-subtitle">TV Price Intelligence Platform</p>
            <div className="brand-features">
              <div className="feature-item">
                <i className="bi bi-check-circle-fill"></i>
                <span>Compare prices across platforms</span>
              </div>
              <div className="feature-item">
                <i className="bi bi-check-circle-fill"></i>
                <span>Track price history & trends</span>
              </div>
              <div className="feature-item">
                <i className="bi bi-check-circle-fill"></i>
                <span>Get best deal alerts</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Form */}
        <div className="auth-form-container">
          <div className="auth-card">
            <div className="auth-header">
              <h2>Welcome Back</h2>
              <p>Sign in to your account</p>
            </div>

            {(formError || error) && (
              <div className="alert alert-danger alert-dismissible fade show">
                <i className="bi bi-exclamation-circle me-2"></i>
                {formError || error}
                <button type="button" className="btn-close" onClick={() => setFormError("")}></button>
              </div>
            )}

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-floating mb-3">
                <input
                  type="email"
                  className="form-control"
                  id="email"
                  name="email"
                  placeholder="Email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  disabled={isSubmitting}
                />
                <label htmlFor="email">
                  <i className="bi bi-envelope me-2"></i>Email address
                </label>
              </div>

              <div className="form-floating mb-3 password-field">
                <input
                  type={showPassword ? "text" : "password"}
                  className="form-control"
                  id="password"
                  name="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  disabled={isSubmitting}
                />
                <label htmlFor="password">
                  <i className="bi bi-lock me-2"></i>Password
                </label>
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                >
                  <i className={`bi ${showPassword ? "bi-eye-slash" : "bi-eye"}`}></i>
                </button>
              </div>

              <div className="d-flex justify-content-between align-items-center mb-4">
                <div className="form-check">
                  <input type="checkbox" className="form-check-input" id="remember" />
                  <label className="form-check-label" htmlFor="remember">
                    Remember me
                  </label>
                </div>
                <Link to="/forgot-password" className="forgot-link">
                  Forgot password?
                </Link>
              </div>

              <button
                type="submit"
                className="btn btn-primary btn-auth w-100"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2"></span>
                    Signing in...
                  </>
                ) : (
                  <>
                    <i className="bi bi-box-arrow-in-right me-2"></i>
                    Sign In
                  </>
                )}
              </button>
            </form>

            <div className="auth-footer">
              <p>
                Don't have an account?{" "}
                <Link to="/register" className="auth-link">
                  Create account
                </Link>
              </p>
            </div>

            {/* Demo Credentials */}
            <div className="demo-credentials">
              <p className="demo-title">Demo Credentials</p>
              <div className="demo-info">
                <small><strong>Admin:</strong> admin@offerzone.com / Admin@123</small>
                <small><strong>User:</strong> user@offerzone.com / User@123</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;