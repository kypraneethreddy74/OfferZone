/**
 * Authentication Context Provider with Email Verification
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { authAPI } from "../services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check auth on mount
  const checkAuth = useCallback(async () => {
    try {
      setLoading(true);
      const response = await authAPI.getMe();
      setUser(response.data);
      setError(null);
    } catch (err) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();

    const handleLogout = () => {
      setUser(null);
      setError("Session expired. Please login again.");
    };

    window.addEventListener("auth:logout", handleLogout);
    return () => window.removeEventListener("auth:logout", handleLogout);
  }, [checkAuth]);

  const login = async (credentials) => {
    try {
      setLoading(true);
      setError(null);
      const response = await authAPI.login(credentials);
      if (response.data.success) {
        setUser(response.data.user);
        return { 
          success: true, 
          requiresVerification: response.data.requires_verification 
        };
      }
      throw new Error(response.data.message || "Login failed");
    } catch (err) {
      const message = err.response?.data?.detail || err.message || "Login failed";
      setError(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await authAPI.register(userData);
      if (response.data.success) {
        setUser(response.data.user);
        return { 
          success: true, 
          requiresVerification: response.data.requires_verification,
          message: response.data.message
        };
      }
      throw new Error(response.data.message || "Registration failed");
    } catch (err) {
      const message = err.response?.data?.detail || err.message || "Registration failed";
      setError(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (err) {
      console.error("Logout error:", err);
    } finally {
      setUser(null);
      setError(null);
    }
  };

// In AuthContext.js, update the verifyEmail function:

  const verifyEmail = async (token) => {
    try {
      setLoading(true);
      const response = await authAPI.verifyEmail(token);
    
      if (response.data.success) {
        // Refresh user data to get updated verification status
        await checkAuth();
        return { success: true, message: response.data.message };
      }
    
      return { success: false, error: response.data.message || "Verification failed" };
    } catch (err) {
      const errorDetail = err.response?.data?.detail || err.message || "Verification failed";
    
      // Don't treat "already verified" as an error
      if (errorDetail.toLowerCase().includes("already")) {
        return { success: false, error: errorDetail, alreadyVerified: true };
      }
    
      return { success: false, error: errorDetail };
    } finally {
      setLoading(false);
    }
  };

  // NEW: Resend Verification
  const resendVerification = async (email) => {
    try {
      const response = await authAPI.resendVerification(email);
      return { success: true, message: response.data.message };
    } catch (err) {
      const message = err.response?.data?.detail || err.message || "Failed to resend";
      return { success: false, error: message };
    }
  };

  // NEW: Forgot Password
  const forgotPassword = async (email) => {
    try {
      const response = await authAPI.forgotPassword(email);
      return { success: true, message: response.data.message };
    } catch (err) {
      const message = err.response?.data?.detail || err.message || "Request failed";
      return { success: false, error: message };
    }
  };

  // NEW: Reset Password
  const resetPassword = async (data) => {
    try {
      const response = await authAPI.resetPassword(data);
      return { success: true, message: response.data.message };
    } catch (err) {
      const message = err.response?.data?.detail || err.message || "Reset failed";
      return { success: false, error: message };
    }
  };

  const clearError = () => setError(null);

  const isAdmin = () => user?.role === "admin";
  
  // NEW: Check if user is verified
  const isVerified = () => user?.is_verified === true;

  const value = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    isVerified,
    login,
    register,
    logout,
    checkAuth,
    clearError,
    isAdmin,
    // NEW methods
    verifyEmail,
    resendVerification,
    forgotPassword,
    resetPassword,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};

export default AuthContext;