/**
 * Navigation Bar with Authentication
 */


import React, { useState } from "react";
import { NavLink, Link, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import "./Navbar.css";
import { useWishlist } from "../context/WishlistContext";

function Navbar() {
  const { user, isAuthenticated, logout, isAdmin } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const navigate = useNavigate();
  const { count } = useWishlist();

  const handleLogout = async () => {
    setIsLoggingOut(true);
    await logout();
    setIsLoggingOut(false);
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark offerzone-navbar sticky-top">
      <div className="container-fluid">
        {/* BRAND LOGO */}
        <NavLink to="/" className="navbar-brand offerzone-logo">
          <i className="bi bi-tv me-2"></i>
          OfferZone
        </NavLink>

        {/* MOBILE TOGGLE */}
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#offerzoneNav"
          aria-controls="offerzoneNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        {/* NAV LINKS */}
        <div className="collapse navbar-collapse" id="offerzoneNav">
          <ul className="navbar-nav ms-auto gap-lg-2 align-items-lg-center">
            {/* PUBLIC LINKS */}
            <li className="nav-item">
              <NavLink to="/catalog" className="nav-link">
                <i className="bi bi-grid me-1"></i>Catalog
              </NavLink>
            </li>
              
            <li className="nav-item">
              <NavLink to="/best-deals" className="nav-link">
                <i className="bi bi-tag me-1"></i>Best Deals
              </NavLink>
            </li>

            <li className="nav-item">
              <NavLink to="/compare" className="nav-link">
                <i className="bi bi-arrow-left-right me-1"></i>Compare
              </NavLink>
            </li>

            <li className="nav-item">
              <NavLink to="/filters" className="nav-link">
                <i className="bi bi-funnel me-1"></i>Filters
              </NavLink>
            </li>
			
			
			<Link to="/wishlist" className="nav-link wishlist-link">
			  <span className="wishlist-icon">❤️</span>
			  {count > 0 && <span className="wishlist-badge">{count}</span>}
			</Link>

            {/* AUTHENTICATED USER LINKS */}
            {isAuthenticated && (
              <>
                <li className="nav-item">
                  <NavLink to="/graphs" className="nav-link">
                    <i className="bi bi-bar-chart me-1"></i>Graphs
                  </NavLink>
                </li>

                {/* ADMIN ONLY LINKS */}
                {isAdmin() && (
                  <li className="nav-item">
                    <NavLink to="/statistics" className="nav-link">
                      <i className="bi bi-graph-up me-1"></i>Statistics
                    </NavLink>
                  </li>
                  
                )}
              </>
            )}

            {/* DIVIDER */}
            <li className="nav-item d-none d-lg-block">
              <span className="nav-divider"></span>
            </li>

            {/* AUTH SECTION */}
            {isAuthenticated ? (
              /* USER DROPDOWN */
              <li className="nav-item dropdown">
                <button
                  className="btn nav-link dropdown-toggle user-dropdown"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  <div className="user-avatar">
                    {user?.name?.charAt(0).toUpperCase()}
                  </div>
                  <span className="user-name d-none d-lg-inline">
                    {user?.name}
                  </span>
                  {isAdmin() && (
                    <span className="badge bg-warning text-dark ms-1 badge-admin">
                      Admin
                    </span>
                  )}
                </button>
                <ul className="dropdown-menu dropdown-menu-end">
                  <li>
                    <div className="dropdown-header">
                      <strong>{user?.name}</strong>
                      <small className="d-block text-muted">{user?.email}</small>
                    </div>
                  </li>
                  <li><hr className="dropdown-divider" /></li>
                  <li>
                    <NavLink to="/profile" className="dropdown-item">
                      <i className="bi bi-person me-2"></i>Profile
                    </NavLink>
                  </li>
                  <li>
                    <NavLink to="/settings" className="dropdown-item">
                      <i className="bi bi-gear me-2"></i>Settings
                    </NavLink>
                  </li>
                  {isAdmin() && (
                    <>
                      <li><hr className="dropdown-divider" /></li>
                      <li>
                        <NavLink to="/admin" className="dropdown-item">
                          <i className="bi bi-shield-lock me-2"></i>Admin Panel
                        </NavLink>
                      </li>
                    </>
                  )}
                  <li><hr className="dropdown-divider" /></li>
                  <li>
                    <button
                      className="dropdown-item text-danger"
                      onClick={handleLogout}
                      disabled={isLoggingOut}
                    >
                      {isLoggingOut ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2"></span>
                          Logging out...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-box-arrow-right me-2"></i>
                          Logout
                        </>
                      )}
                    </button>
                  </li>
                </ul>
              </li>
            ) : (
              /* LOGIN/REGISTER BUTTONS */
              <>
                <li className="nav-item">
                  <NavLink to="/login" className="nav-link">
                    <i className="bi bi-box-arrow-in-right me-1"></i>Login
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink to="/register" className="btn btn-register">
                    <i className="bi bi-person-plus me-1"></i>Register
                  </NavLink>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;