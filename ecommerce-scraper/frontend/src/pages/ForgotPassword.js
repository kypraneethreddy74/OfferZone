/**
 * Forgot Password Page
 */

import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Auth.css";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  const { forgotPassword } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError("");

    const result = await forgotPassword(email);
    
    if (result.success) {
      setSubmitted(true);
    } else {
      setError(result.error);
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
                <i className="bi bi-shield-lock-fill"></i>
                <span>Secure password reset</span>
              </div>
              <div className="feature-item">
                <i className="bi bi-envelope-check"></i>
                <span>Email verification</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Form */}
        <div className="auth-form-container">
          <div className="auth-card">
            {!submitted ? (
              <>
                <div className="auth-header">
                  <h2>Forgot Password?</h2>
                  <p>Enter your email to receive a reset link</p>
                </div>

                {error && (
                  <div className="alert alert-danger alert-dismissible fade show">
                    <i className="bi bi-exclamation-circle me-2"></i>
                    {error}
                    <button type="button" className="btn-close" onClick={() => setError("")}></button>
                  </div>
                )}

                <form onSubmit={handleSubmit} className="auth-form">
                  <div className="form-floating mb-4">
                    <input
                      type="email"
                      className="form-control"
                      id="email"
                      placeholder="Email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      disabled={isSubmitting}
                    />
                    <label htmlFor="email">
                      <i className="bi bi-envelope me-2"></i>Email address
                    </label>
                  </div>

                  <button
                    type="submit"
                    className="btn btn-primary btn-auth w-100"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Sending...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-send me-2"></i>
                        Send Reset Link
                      </>
                    )}
                  </button>
                </form>

                <div className="auth-footer">
                  <p>
                    Remember your password?{" "}
                    <Link to="/login" className="auth-link">
                      Back to Login
                    </Link>
                  </p>
                </div>
              </>
            ) : (
              <>
                <div className="text-center">
                  <div className="mb-4">
                    <i className="bi bi-envelope-check text-success" style={{ fontSize: "4rem" }}></i>
                  </div>
                  <h2 className="mb-3">Check Your Email</h2>
                  <p className="text-muted mb-4">
                    If an account exists with <strong>{email}</strong>, you'll receive a password reset link shortly.
                  </p>
                  <div className="alert alert-info">
                    <i className="bi bi-info-circle me-2"></i>
                    The link will expire in 1 hour.
                  </div>
                  <div className="mt-4">
                    <Link to="/login" className="btn btn-primary btn-auth">
                      <i className="bi bi-box-arrow-in-right me-2"></i>
                      Back to Login
                    </Link>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;