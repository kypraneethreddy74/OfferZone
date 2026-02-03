/**
 * Email Verification Page - FIXED VERSION
 * Prevents multiple API calls
 */

import React, { useEffect, useState, useRef } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Auth.css";

const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { verifyEmail, user, isVerified, checkAuth } = useAuth();
  
  const [status, setStatus] = useState("verifying"); // verifying, success, error, already_verified
  const [message, setMessage] = useState("");
  
  // Use ref to prevent multiple API calls
  const hasVerified = useRef(false);

  const token = searchParams.get("token");

  useEffect(() => {
    // Prevent multiple calls
    if (hasVerified.current) {
      return;
    }

    const verify = async () => {
      // No token provided
      if (!token) {
        setStatus("error");
        setMessage("Invalid verification link. No token provided.");
        return;
      }

      // Mark as called to prevent re-execution
      hasVerified.current = true;

      try {
        const result = await verifyEmail(token);
        
        if (result.success) {
          setStatus("success");
          setMessage(result.message || "Email verified successfully!");
          
          // Refresh auth state
          await checkAuth();
          
          // Redirect after 3 seconds
          setTimeout(() => {
            navigate("/", { replace: true });
          }, 3000);
        } else {
          // Check if it's "already verified" or "already used"
          const errorMsg = result.error || "Verification failed";
          
          if (errorMsg.toLowerCase().includes("already")) {
            setStatus("already_verified");
            setMessage("This email has already been verified. You can log in now.");
          } else {
            setStatus("error");
            setMessage(errorMsg);
          }
        }
      } catch (err) {
        setStatus("error");
        setMessage("An error occurred during verification. Please try again.");
      }
    };

    verify();
  }, [token]); // Only depend on token, not on verifyEmail or other functions

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

        {/* Right Side - Status */}
        <div className="auth-form-container">
          <div className="auth-card text-center">
            
            {/* Verifying State */}
            {status === "verifying" && (
              <>
                <div className="verification-icon verifying">
                  <div className="spinner-border text-warning" role="status" style={{ width: "4rem", height: "4rem" }}>
                    <span className="visually-hidden">Loading...</span>
                  </div>
                </div>
                <h2 className="mt-4">Verifying your email...</h2>
                <p className="text-muted">Please wait while we verify your email address.</p>
              </>
            )}

            {/* Success State */}
            {status === "success" && (
              <>
                <div className="verification-icon success">
                  <i className="bi bi-check-circle-fill text-success" style={{ fontSize: "5rem" }}></i>
                </div>
                <h2 className="mt-4 text-success">Email Verified! 🎉</h2>
                <p className="text-muted">{message}</p>
                <p className="text-muted">Redirecting to homepage in 3 seconds...</p>
                <div className="mt-4">
                  <Link to="/best-deals" className="btn btn-primary btn-auth me-2">
                    <i className="bi bi-tag me-2"></i>
                    Browse Deals
                  </Link>
                  <Link to="/" className="btn btn-outline-secondary">
                    <i className="bi bi-house me-2"></i>
                    Go Home
                  </Link>
                </div>
              </>
            )}

            {/* Already Verified State */}
            {status === "already_verified" && (
              <>
                <div className="verification-icon">
                  <i className="bi bi-check-circle-fill text-info" style={{ fontSize: "5rem" }}></i>
                </div>
                <h2 className="mt-4 text-info">Already Verified</h2>
                <p className="text-muted">{message}</p>
                <div className="mt-4">
                  <Link to="/login" className="btn btn-primary btn-auth me-2">
                    <i className="bi bi-box-arrow-in-right me-2"></i>
                    Login
                  </Link>
                  <Link to="/best-deals" className="btn btn-outline-secondary">
                    <i className="bi bi-tag me-2"></i>
                    Browse Deals
                  </Link>
                </div>
              </>
            )}

            {/* Error State */}
            {status === "error" && (
              <>
                <div className="verification-icon error">
                  <i className="bi bi-x-circle-fill text-danger" style={{ fontSize: "5rem" }}></i>
                </div>
                <h2 className="mt-4 text-danger">Verification Failed</h2>
                <p className="text-muted">{message}</p>
                <div className="mt-4">
                  <Link to="/login" className="btn btn-primary btn-auth me-2">
                    <i className="bi bi-box-arrow-in-right me-2"></i>
                    Login
                  </Link>
                  <Link to="/resend-verification" className="btn btn-outline-warning">
                    <i className="bi bi-envelope me-2"></i>
                    Resend Email
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

export default VerifyEmail;