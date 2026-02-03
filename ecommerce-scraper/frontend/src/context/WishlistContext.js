/**
 * Wishlist Context Provider
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { wishlistAPI } from "../services/api";
import { useAuth } from "./AuthContext";

const WishlistContext = createContext(null);

export const WishlistProvider = ({ children }) => {
  const { user, isVerified } = useAuth();
  const [wishlist, setWishlist] = useState([]);
  const [wishlistIds, setWishlistIds] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState(0);

  // Fetch wishlist when user logs in
  const fetchWishlist = useCallback(async () => {
    if (!user) {
      setWishlist([]);
      setWishlistIds(new Set());
      setCount(0);
      return;
    }

    try {
      setLoading(true);
      const response = await wishlistAPI.getWishlist();
      const items = response.data.items || [];
      setWishlist(items);
      setWishlistIds(new Set(items.map(item => item.model_id)));
      setCount(items.length);
    } catch (err) {
      console.error("Failed to fetch wishlist:", err);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchWishlist();
  }, [fetchWishlist]);

  // Check if product is in wishlist
  const isInWishlist = useCallback((modelId) => {
    return wishlistIds.has(modelId);
  }, [wishlistIds]);

  // Toggle wishlist
  const toggleWishlist = async (modelId) => {
    if (!user) {
      return { success: false, error: "Please login to add to wishlist" };
    }

    if (!isVerified()) {
      return { success: false, error: "Please verify your email to use wishlist" };
    }

    try {
      const response = await wishlistAPI.toggle(modelId);
      
      if (response.data.success) {
        if (response.data.action === "added") {
          setWishlistIds(prev => new Set([...prev, modelId]));
          setCount(prev => prev + 1);
        } else {
          setWishlistIds(prev => {
            const newSet = new Set(prev);
            newSet.delete(modelId);
            return newSet;
          });
          setCount(prev => prev - 1);
        }
        
        // Refresh full wishlist in background
        fetchWishlist();
        
        return { success: true, action: response.data.action };
      }
      
      return { success: false, error: "Failed to update wishlist" };
    } catch (err) {
      const message = err.response?.data?.detail || "Failed to update wishlist";
      return { success: false, error: message };
    }
  };

  // Remove from wishlist
  const removeFromWishlist = async (modelId) => {
    try {
      await wishlistAPI.removeFromWishlist(modelId);
      setWishlistIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(modelId);
        return newSet;
      });
      setWishlist(prev => prev.filter(item => item.model_id !== modelId));
      setCount(prev => prev - 1);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || "Failed to remove" };
    }
  };

  // Bulk check for product listing pages
  const checkBulkStatus = async (modelIds) => {
    if (!user || modelIds.length === 0) return;
    
    try {
      const response = await wishlistAPI.checkBulk(modelIds);
      const wishlisted = new Set(response.data.wishlisted || []);
      setWishlistIds(prev => new Set([...prev, ...wishlisted]));
    } catch (err) {
      console.error("Bulk check failed:", err);
    }
  };

  const value = {
    wishlist,
    wishlistIds,
    count,
    loading,
    isInWishlist,
    toggleWishlist,
    removeFromWishlist,
    fetchWishlist,
    checkBulkStatus,
  };

  return (
    <WishlistContext.Provider value={value}>
      {children}
    </WishlistContext.Provider>
  );
};

export const useWishlist = () => {
  const context = useContext(WishlistContext);
  if (!context) {
    throw new Error("useWishlist must be used within WishlistProvider");
  }
  return context;
};

export default WishlistContext;