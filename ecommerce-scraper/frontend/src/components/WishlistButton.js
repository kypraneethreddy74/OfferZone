/**
 * Wishlist Heart Button Component
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useWishlist } from "../context/WishlistContext";
import "./WishlistButton.css";

const WishlistButton = ({ modelId, size = "md", showText = false }) => {
  const navigate = useNavigate();
  const { user, isVerified } = useAuth();
  const { isInWishlist, toggleWishlist } = useWishlist();
  
  const [loading, setLoading] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const [tooltipMessage, setTooltipMessage] = useState("");

  const inWishlist = isInWishlist(modelId);

  const handleClick = async (e) => {
    e.stopPropagation();
    e.preventDefault();

    // Not logged in
    if (!user) {
      setTooltipMessage("Login to add to wishlist");
      setShowTooltip(true);
      setTimeout(() => setShowTooltip(false), 2000);
      setTimeout(() => navigate("/login"), 1000);
      return;
    }

    // Not verified
    if (!isVerified()) {
      setTooltipMessage("Verify email to use wishlist");
      setShowTooltip(true);
      setTimeout(() => setShowTooltip(false), 2000);
      return;
    }

    setLoading(true);
    const result = await toggleWishlist(modelId);
    setLoading(false);

    if (result.success) {
      setTooltipMessage(result.action === "added" ? "Added!" : "Removed!");
      setShowTooltip(true);
      setTimeout(() => setShowTooltip(false), 1500);
    } else {
      setTooltipMessage(result.error);
      setShowTooltip(true);
      setTimeout(() => setShowTooltip(false), 2000);
    }
  };

  return (
    <div className="wishlist-btn-wrapper">
      <button
        className={`wishlist-btn wishlist-btn-${size} ${inWishlist ? "active" : ""} ${loading ? "loading" : ""}`}
        onClick={handleClick}
        disabled={loading}
        aria-label={inWishlist ? "Remove from wishlist" : "Add to wishlist"}
      >
        {loading ? (
          <span className="spinner-border spinner-border-sm"></span>
        ) : (
          <>
            <span className="heart-icon">{inWishlist ? "❤️" : "🤍"}</span>
            {showText && (
              <span className="btn-text">
                {inWishlist ? "Saved" : "Save"}
              </span>
            )}
          </>
        )}
      </button>
      
      {showTooltip && (
        <div className="wishlist-tooltip">{tooltipMessage}</div>
      )}
    </div>
  );
};

export default WishlistButton;