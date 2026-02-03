/**
 * Reset Password Page
 */

import React, { useState, useEffect } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Auth.css";

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { resetPassword } = useAuth();
  
  const [formData, setFormData] = useState({
    password: "",
    confirm_password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [passwordStrength, setPasswordStrength] = useState(0);

  const token = searchParams.get("token");

  // Redirect if no token
  useEffect(() => {
    if (!token) {
      navigate("/forgot-password", { replace: true });
    }
  }, [token, navigate]);

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
    setError("");
  };

  const validateForm = () => {
    const errors = {};
    
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
    setError("");

    const result = await resetPassword({
      token,
      password: formData.password,
      confirm_password: formData.confirm_password,
    });
    
    if (result.success) {
      setSuccess(true);
    } else {
      setError(result.error);
    }
    
    setIsSubmitting(false);
  };

  if (!token) return null;

  return (
    <div className="auth-page">
      <div className="auth-container">
        {/* Left Side - Branding */}
        <div className="auth-branding">
          <div className="brand-content">
            <h1 className="brand-title">OfferZone</h1>
            <p className="brand-subtitle">TV Price Intelligence Platform</p>
          </div>
        </div>

        {/* Right Side - Form */}
        <div className="auth-form-container">
          <div className="auth-card">
            {!success ? (
              <>
                <div className="auth-header">
                  <h2>Reset Password</h2>
                  <p>Create a new secure password</p>
                </div>

                {error && (
                  <div className="alert alert-danger alert-dismissible fade show">
                    <i className="bi bi-exclamation-circle me-2"></i>
                    {error}
                    <button type="button" className="btn-close" onClick={() => setError("")}></button>
                  </div>
                )}

                <form onSubmit={handleSubmit} className="auth-form">
                  {/* Password Field */}
                  <div className="form-floating mb-2 password-field">
                    <input
                      type={showPassword ? "text" : "password"}
                      className={`form-control ${fieldErrors.password ? "is-invalid" : ""}`}
                      id="password"
                      name="password"
                      placeholder="New Password"
                      value={formData.password}
                      onChange={handleChange}
                      disabled={isSubmitting}
                    />
                    <label htmlFor="password">
                      <i className="bi bi-lock me-2"></i>New Password
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

                  <button
                    type="submit"
                    className="btn btn-primary btn-auth w-100"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Resetting...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check-lg me-2"></i>
                        Reset Password
                      </>
                    )}
                  </button>
                </form>
              </>
            ) : (
              <>
                <div className="text-center">
                  <div className="mb-4">
                    <i className="bi bi-check-circle-fill text-success" style={{ fontSize: "4rem" }}></i>
                  </div>
                  <h2 className="mb-3 text-success">Password Reset Successfully!</h2>
                  <p className="text-muted mb-4">
                    Your password has been changed. You can now log in with your new password.
                  </p>
                  <Link to="/login" className="btn btn-primary btn-auth">
                    <i className="bi bi-box-arrow-in-right me-2"></i>
                    Go to Login
                  </Link>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;