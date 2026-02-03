/**
 * Verification Banner Component
 * Shows when user is logged in but not verified
 */

import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import "./VerificationBanner.css";

const VerificationBanner = () => {
  const { user, isVerified, resendVerification } = useAuth();
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  // Don't show if not logged in, already verified, or dismissed
  if (!user || isVerified() || dismissed) {
    return null;
  }

  const handleResend = async () => {
    setSending(true);
    const result = await resendVerification(user.email);
    setSending(false);
    if (result.success) {
      setSent(true);
      setTimeout(() => setSent(false), 5000);
    }
  };

  return (
    <div className="verification-banner">
      <div className="container">
        <div className="banner-content">
          <div className="banner-icon">
            <i className="bi bi-envelope-exclamation"></i>
          </div>
          <div className="banner-text">
            <strong>Verify your email</strong>
            <span>Please verify your email to access all features like wishlist and price alerts.</span>
          </div>
          <div className="banner-actions">
            {sent ? (
              <span className="sent-message">
                <i className="bi bi-check-circle me-1"></i>
                Email sent!
              </span>
            ) : (
              <button
                className="btn btn-sm btn-light"
                onClick={handleResend}
                disabled={sending}
              >
                {sending ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-1"></span>
                    Sending...
                  </>
                ) : (
                  <>
                    <i className="bi bi-envelope me-1"></i>
                    Resend Email
                  </>
                )}
              </button>
            )}
            <button
              className="btn btn-sm btn-link text-white"
              onClick={() => setDismissed(true)}
            >
              <i className="bi bi-x-lg"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerificationBanner;