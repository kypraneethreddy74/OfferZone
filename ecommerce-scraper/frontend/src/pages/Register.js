/**
 * Register Page - Premium SaaS Design
 */

import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Auth.css";

const Register = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formError, setFormError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);

  const { register, error, clearError } = useAuth();
  const navigate = useNavigate();

  // Password strength calculator
  useEffect(() => {
    const password = formData.password;
    let strength = 0;
    
    if (password.length >= 8) strength += 25;
    if (/[A-Z]/.test(password)) strength += 25;
    if (/[a-z]/.test(password)) strength += 25;
    if (/[0-9]/.test(password)) strength += 12.5;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength += 12.5;
    
    setPasswordStrength(strength);
  }, [formData.password]);

  const getStrengthColor = () => {
    if (passwordStrength <= 25) return "danger";
    if (passwordStrength <= 50) return "warning";
    if (passwordStrength <= 75) return "info";
    return "success";
  };

  const getStrengthText = () => {
    if (passwordStrength <= 25) return "Weak";
    if (passwordStrength <= 50) return "Fair";
    if (passwordStrength <= 75) return "Good";
    return "Strong";
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    setFieldErrors({ ...fieldErrors, [name]: "" });
    setFormError("");
    clearError();
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.name.trim()) {
      errors.name = "Name is required";
    }
    
    if (!formData.email.trim()) {
      errors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = "Invalid email format";
    }
    
    if (!formData.password) {
      errors.password = "Password is required";
    } else if (formData.password.length < 8) {
      errors.password = "Password must be at least 8 characters";
    } else if (!/[A-Z]/.test(formData.password)) {
      errors.password = "Password must contain an uppercase letter";
    } else if (!/[a-z]/.test(formData.password)) {
      errors.password = "Password must contain a lowercase letter";
    } else if (!/[0-9]/.test(formData.password)) {
      errors.password = "Password must contain a number";
    } else if (!/[!@#$%^&*(),.?":{}|<>]/.test(formData.password)) {
      errors.password = "Password must contain a special character";
    }
    
    if (formData.password !== formData.confirm_password) {
      errors.confirm_password = "Passwords do not match";
    }
    
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsSubmitting(true);
    setFormError("");

    const result = await register(formData);
    
    if (result.success) {
      navigate("/", { replace: true });
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
            <p className="brand-subtitle">Join thousands of smart shoppers</p>
            <div className="brand-features">
              <div className="feature-item">
                <i className="bi bi-graph-up-arrow"></i>
                <span>Real-time price tracking</span>
              </div>
              <div className="feature-item">
                <i className="bi bi-bell-fill"></i>
                <span>Price drop notifications</span>
              </div>
              <div className="feature-item">
                <i className="bi bi-shield-check"></i>
                <span>Secure & private</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Form */}
        <div className="auth-form-container">
          <div className="auth-card">
            <div className="auth-header">
              <h2>Create Account</h2>
              <p>Start saving on your TV purchases</p>
            </div>

            {(formError || error) && (
              <div className="alert alert-danger alert-dismissible fade show">
                <i className="bi bi-exclamation-circle me-2"></i>
                {formError || error}
                <button type="button" className="btn-close" onClick={() => setFormError("")}></button>
              </div>
            )}

            <form onSubmit={handleSubmit} className="auth-form">
              {/* Name Field */}
              <div className="form-floating mb-3">
                <input
                  type="text"
                  className={`form-control ${fieldErrors.name ? "is-invalid" : ""}`}
                  id="name"
                  name="name"
                  placeholder="Full Name"
                  value={formData.name}
                  onChange={handleChange}
                  disabled={isSubmitting}
                />
                <label htmlFor="name">
                  <i className="bi bi-person me-2"></i>Full Name
                </label>
                {fieldErrors.name && (
                  <div className="invalid-feedback">{fieldErrors.name}</div>
                )}
              </div>

              {/* Email Field */}
              <div className="form-floating mb-3">
                <input
                  type="email"
                  className={`form-control ${fieldErrors.email ? "is-invalid" : ""}`}
                  id="email"
                  name="email"
                  placeholder="Email"
                  value={formData.email}
                  onChange={handleChange}
                  disabled={isSubmitting}
                />
                <label htmlFor="email">
                  <i className="bi bi-envelope me-2"></i>Email address
                </label>
                {fieldErrors.email && (
                  <div className="invalid-feedback">{fieldErrors.email}</div>
                )}
              </div>

              {/* Password Field */}
              <div className="form-floating mb-2 password-field">
                <input
                  type={showPassword ? "text" : "password"}
                  className={`form-control ${fieldErrors.password ? "is-invalid" : ""}`}
                  id="password"
                  name="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={handleChange}
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
                {fieldErrors.password && (
                  <div className="invalid-feedback">{fieldErrors.password}</div>
                )}
              </div>

              {/* Password Strength */}
              {formData.password && (
                <div className="password-strength mb-3">
                  <div className="progress" style={{ height: "4px" }}>
                    <div
                      className={`progress-bar bg-${getStrengthColor()}`}
                      style={{ width: `${passwordStrength}%` }}
                    ></div>
                  </div>
                  <small className={`text-${getStrengthColor()}`}>
                    Password strength: {getStrengthText()}
                  </small>
                </div>
              )}

              {/* Confirm Password Field */}
              <div className="form-floating mb-4 password-field">
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  className={`form-control ${fieldErrors.confirm_password ? "is-invalid" : ""}`}
                  id="confirm_password"
                  name="confirm_password"
                  placeholder="Confirm Password"
                  value={formData.confirm_password}
                  onChange={handleChange}
                  disabled={isSubmitting}
                />
                <label htmlFor="confirm_password">
                  <i className="bi bi-lock-fill me-2"></i>Confirm Password
                </label>
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  tabIndex={-1}
                >
                  <i className={`bi ${showConfirmPassword ? "bi-eye-slash" : "bi-eye"}`}></i>
                </button>
                {fieldErrors.confirm_password && (
                  <div className="invalid-feedback">{fieldErrors.confirm_password}</div>
                )}
              </div>

              {/* Terms */}
              <div className="form-check mb-4">
                <input type="checkbox" className="form-check-input" id="terms" required />
                <label className="form-check-label" htmlFor="terms">
                  I agree to the <Link to="/terms">Terms of Service</Link> and{" "}
                  <Link to="/privacy">Privacy Policy</Link>
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
                    Creating account...
                  </>
                ) : (
                  <>
                    <i className="bi bi-person-plus me-2"></i>
                    Create Account
                  </>
                )}
              </button>
            </form>

            <div className="auth-footer">
              <p>
                Already have an account?{" "}
                <Link to="/login" className="auth-link">
                  Sign in
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;